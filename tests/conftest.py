import sys
from pathlib import Path

import pytest
from ape import accounts, networks

sys.path.insert(0, str(Path(__file__).parent.parent))

from services import FactoryDeployerService


@pytest.fixture
def deployer(accounts):
    """Pre-funded test account for deploying contracts."""
    return accounts[0]


@pytest.fixture
def admin(accounts):
    """Account to act as delegation contract admin."""
    return accounts[1]


@pytest.fixture
def delegatee(accounts):
    """Account to act as delegation contract delegatee."""
    return accounts[2]


@pytest.fixture
def mainnet_fork():
    """Mainnet fork network context."""
    with networks.ethereum.mainnet_fork.use_provider("foundry"):
        yield


@pytest.fixture
def delegation_factory_contract(mainnet_fork, deployer):
    """Deploy DelegationFactory via FactoryDeployerService."""
    result = FactoryDeployerService(deployer).execute()
    return result.contract
