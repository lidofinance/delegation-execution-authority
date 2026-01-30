// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

interface IDelegationContract {
    event DelegateAssigned(address indexed delegate);
    event DelegateRevoked(address indexed delegate);
    event AdminChanged(address indexed oldAdmin, address indexed newAdmin);

    error NotAdmin();
    error NotDelegatee();
    error ZeroAddress();
    error SameDelegatee();
    error SameAdmin();
    error NoDelegatee();
    error InvalidSignature();
    error DelegatecallFailed();

    function admin() external view returns (address);
    function delegatee() external view returns (address);

    function assignDelegate(address delegate) external;
    function revokeDelegate() external;
    function changeAdmin(address newAdmin) external;

    /// @notice EIP-1271 signature validation
    /// @param hash The hash of the data to be signed
    /// @param signature The signature bytes
    /// @return magicValue Returns 0x1626ba7e if valid, 0xffffffff otherwise
    function isValidSignature(bytes32 hash, bytes calldata signature) external view returns (bytes4 magicValue);

    /// @notice Execute a call to a target contract on behalf of this delegation contract
    /// @param data ABI-encoded as (address target, bytes calldata) - the target contract and calldata to execute
    /// @return result The return data from the call
    function delegatecall(bytes calldata data) external returns (bytes memory result);
}
