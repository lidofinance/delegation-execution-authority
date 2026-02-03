// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

import {IDelegationFactory} from "./interfaces/IDelegationFactory.sol";
import {DelegationContract} from "./DelegationContract.sol";

/// @title DelegationFactory
/// @author Lido
/// @notice Factory for deploying DelegationContract instances
/// @dev Deploys standardized delegation contracts for permissioned entities
contract DelegationFactory is IDelegationFactory {
    /// @inheritdoc IDelegationFactory
    function deployDelegation(address admin, address delegatee) external returns (address) {
        DelegationContract delegation = new DelegationContract(admin, delegatee);

        emit DelegationDeployed(admin, address(delegation));

        return address(delegation);
    }
}
