# <img src="docs/logo.svg" height="70px" align="center" alt="Lido Logo"/> Delegation Execution Authority

## WIP

Fast and safe hot-key rotation for Lido Oracles and other permissioned operators.
Overview
- Purpose: Fast and safe hot-key rotation for Lido Oracles and other permissioned operators.
- Concept: A cold wallet or multisig remains the Owner and grants tightly-scoped permissions to hot keys (delegates) for calling specific function selectors on specific target contracts, with optional expiries and value (ETH) limits.
- Outcome: Reduces governance friction and operational overhead for key rotation. Aligns with account abstraction concepts (EIP-7702 inspiration) while keeping a simple, auditable Vyper contract.

Contract
- Path: contracts/DelegatedExecutionAuthority.vy
- Vyper version: 0.4.3
- Core storage:
  - owner (address)
  - allowed[delegate][target][selector] => bool
  - expiry[...], value_limit[...]
  - nonces[delegate] for signature-based grants
- Core methods:
  - set_permission(delegate, target, selector, allowed, expiry, value_limit)
  - set_permissions_batch(delegate, targets[], selectors[], alloweds[], expiries[], value_limits[], count)
  - execute(target, calldata) payable
  - grant_permission_by_sig(delegate, target, selector, allowed, expiry, value_limit, deadline, v, r, s)
  - is_allowed(delegate, target, selector) view
  - get_permission(delegate, target, selector) view
  - ERC-1271 isValidSignature(hash, signature) view

Security Model and Notes
- Least privilege: limit each hot key to the minimal set of selectors and targets they must operate.
- Expiry: set near-term expiries to force periodic renewal.
- Value limit: set to 0 for no ETH transfers or a specific cap if calls require ETH.
- No wildcard allowances: permissions are per 4-byte selector; batch helper aids management.
- Revocation: use set_permission with allowed=false or set an expiry in the past. The revoke_delegate function is intentionally non-iterable since mappings are not iterable; manage via batches.
- Reentrancy: execute uses a simple lock; it forwards external calls—audit target contract behaviors.
- Signature verification: if owner is a contract, ERC-1271 path is used; if EOA, ECDSA recover is used.
- Not a full EIP-7702: this is a practical delegation primitive compatible with AA-like flows.

Prerequisites
- Python 3.11+
- Poetry (optional, recommended) or pip
- eth-ape >= 0.8.36 and ape-vyper plugin
- Node/provider RPC access for your target network (set in Ape)

Install
- Using Poetry:
  - poetry install

Ape Configuration
- See ape-config.yaml. Contracts folder is contracts/.
- Select your network on the CLI with --network, e.g., ethereum:hoodi.

Compile
- ape compile

Deploy
- Create or load an account in Ape (e.g., ape accounts import default or configure a test account).
- Run:
  - ape run scripts/deploy.py --network ethereum:sepolia --owner <OWNER_ADDRESS>
- Output will show the deployed address and the EIP-712 domain separator.

Grant Permissions (Owner)
- Grant permission to a delegate to call a single selector on a target:
  - ape run scripts/grant_delegate.py \
      --network ethereum:sepolia \
      --contract <DEA_ADDRESS> \
      --delegate <DELEGATE_ADDR> \
      --target <TARGET_ADDR> \
      --sig "methodName(argTypes)" \
      --allowed true \
      --expiry 0 \
      --value-limit 0
- Alternatively pass --selector 0x12345678 instead of --sig.
- For revocation, set --allowed false or set an expiry in the past.

Grant via Owner Signature (Gasless Setup)
- The delegate can obtain an off-chain signature from the owner and submit it:
  - Contract method: grant_permission_by_sig(delegate, target, selector, allowed, expiry, value_limit, deadline, v, r, s)
  - The signed message uses EIP-712-like domain:
    - name: DelegatedExecutionAuthority
    - version: 1
    - chainId: current chain.id
    - verifyingContract: the contract address
  - The typed struct:
    Permit(address delegate,address target,bytes4 selector,uint256 expiry,uint256 valueLimit,uint256 nonce,uint256 deadline)
  - Nonce is per-delegate and stored in the contract.

Execute as Delegate
- If allowed, the delegate can forward the call through the contract:
  - ape run scripts/execute_as_delegate.py \
      --network ethereum:sepolia \
      --contract <DEA_ADDRESS> \
      --target <TARGET_ADDR> \
      --sig "methodName(argTypes)" \
      --arg <arg1> [--arg <arg2> ...] \
      --value 0
- Or pass raw --calldata 0x....

Selector Helper
- scripts/grant_delegate.py can compute selector from a signature via --sig.
- scripts/execute_as_delegate.py can encode simple arguments (address, uint256, bool, bytes32). For complex types, supply --calldata directly.

Operational Guidance for Oracles
- Maintain a cold Owner (multisig or hardware wallets).
- Grant permissions to hot keys used by oracle instances to only the specific methods required (e.g., report(), submit(), etc.).
- Set relatively short expiries (e.g., days) and automate renewal via runbooks.
- If a hot key is compromised or rotated, revoke or let the expiry elapse, and grant a new key immediately.

Testing Locally
- Use a local network provider (e.g., anvil via ape anvil).
- Deploy and interact with sample ERC20/ERC721 to test selectors and execution.

Security Considerations
- Carefully scope selectors; avoid granting generic admin methods.
- Monitor Executed and DelegatePermissionUpdated events.
- value_limit restricts ETH forwarding; set to 0 unless strictly needed.
- Ensure target contracts revert with meaningful errors; execute bubbles up failure.

License
- MIT (adjust as appropriate)
