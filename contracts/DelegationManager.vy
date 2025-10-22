# @version 0.4.3
# DelegationManager: time-limited delegated execution to allow-listed targets.
# - The deployer becomes the owner who can grant/revoke delegate permissions.
# - A delegate may execute calls to specific targets and function selectors
#   only while permissions are valid (until expiry) and within value limits.


# ---------------------------
# Events
# ---------------------------

event OwnerUpdated:
    previous_owner: address
    new_owner: address

event PermissionUpdated:
    delegate: address
    target: address
    selector: bytes32  # we store selector as left-padded 4-byte in bytes32 for indexing clarity
    allowed: bool
    expiry: uint256
    value_limit: uint256

event Executed:
    caller: address
    target: address
    selector: bytes32
    value: uint256

# ---------------------------
# Storage
# ---------------------------

owner: public(address)

# We key by:
#   delegate => target => selector(uint256) => Permission
# Note: We store selector as uint256 key converted from 4 bytes.
struct Permission:
    allowed: bool
    expiry: uint256  # 0 means no expiry
    value_limit: uint256  # 0 means unlimited

permissions: HashMap[address, HashMap[address, HashMap[uint256, Permission]]]

# Reentrancy guard
nonreentrant_lock: uint256

# ---------------------------
# Internal helpers
# ---------------------------

@internal
@pure
def _bytes4_to_uint(selector: Bytes[4]) -> uint256:
    # Convert first 4 bytes into uint256 by right-shifting a 32-byte word by 224 bits
    bs: bytes32 = empty(bytes32)
    if len(selector) > 0:
        # Vyper pads Bytes[N] when converting to bytes32
        bs = convert(selector, bytes32)
    return convert(bs, uint256) >> 224

@internal
@pure
def _selector_from_data(data: Bytes[4096]) -> (uint256, bytes32):
    if len(data) >= 4:
        head: Bytes[4] = slice(data, 0, 4)
        key: uint256 = self._bytes4_to_uint(head)
        # also produce bytes32 representation for events
        b32: bytes32 = convert(head, bytes32)
        return key, b32
    else:
        # For empty data, use 0x00000000 as selector
        return 0, empty(bytes32)

@internal
@view
def _is_allowed(delegate: address, target: address, selector_key: uint256, eth_value: uint256) -> bool:
    p: Permission = self.permissions[delegate][target][selector_key]
    if not p.allowed:
        return False
    if p.expiry != 0 and block.timestamp > p.expiry:
        return False
    if p.value_limit != 0 and eth_value > p.value_limit:
        return False
    return True

# ---------------------------
# Constructor and ownership
# ---------------------------

@deploy
def __init__():
    self.owner = msg.sender
    log OwnerUpdated(empty(address), msg.sender)

@external
@view
def is_owner(addr: address) -> bool:
    return addr == self.owner

@external
def transfer_ownership(new_owner: address):
    assert msg.sender == self.owner, "only owner"
    assert new_owner != empty(address), "zero addr"
    log OwnerUpdated(self.owner, new_owner)
    self.owner = new_owner

# ---------------------------
# Permission management (owner-only)
# ---------------------------

@external
def set_permission(delegate: address, target: address, selector: Bytes[4], allowed: bool, expiry: uint256, value_limit: uint256):
    """
    Grant or revoke delegate permission for a target and selector.
    - selector: first 4 bytes of calldata. For ETH sends (empty data), use 0x00000000.
    - expiry: unix timestamp; 0 means no expiry
    - value_limit: max msg.value delegate can send; 0 means unlimited
    """
    assert msg.sender == self.owner, "only owner"
    assert delegate != empty(address), "bad delegate"
    assert target != empty(address), "bad target"

    key: uint256 = self._bytes4_to_uint(selector)
    self.permissions[delegate][target][key] = Permission(
        allowed=allowed,
        expiry=expiry,
        value_limit=value_limit
    )

    # record selector in bytes32 form for the event
    sel_b32: bytes32 = convert(selector, bytes32)
    log PermissionUpdated(delegate, target, sel_b32, allowed, expiry, value_limit)

@external
@view
def get_permission(delegate: address, target: address, selector: Bytes[4]) -> (bool, uint256, uint256):
    key: uint256 = self._bytes4_to_uint(selector)
    p: Permission = self.permissions[delegate][target][key]
    return p.allowed, p.expiry, p.value_limit

# ---------------------------
# Execution by delegate (or owner)
# ---------------------------

@external
@payable
@nonreentrant
def execute(target: address, data: Bytes[4096]) -> Bytes[4096]:
    """
    Execute a call to `target` with `data` and forwarding msg.value.
    Requirements:
    - If caller is owner, bypass permissions.
    - Otherwise caller must be granted permission for (caller, target, selector(data)),
      current time <= expiry (unless expiry==0), and msg.value <= value_limit (unless 0).
    - Reverts on external call failure.
    Returns the raw return data from the call (truncated to 4096 bytes max).
    """
    assert target != empty(address), "bad target"

    sel_key: uint256 = 0
    sel_b32: bytes32 = empty(bytes32)
    sel_key, sel_b32 = self._selector_from_data(data)

    if msg.sender != self.owner:
        assert self._is_allowed(msg.sender, target, sel_key, msg.value), "not allowed"

    # Make the external call; revert on failure to bubble up
    # max_outsize is bounded for safety. Adjust if needed.
    ret: Bytes[4096] = raw_call(
        target,
        data,
        value=msg.value,
        max_outsize=4096,
        revert_on_failure=True
    )

    log Executed(msg.sender, target, sel_b32, msg.value)
    return ret
