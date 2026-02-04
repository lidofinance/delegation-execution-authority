from dataclasses import dataclass
from enum import Enum

from ape import networks, project
from ape.api import AccountAPI


class Network(str, Enum):
    MAINNET = "mainnet"
    TESTNET = "testnet"

    @property
    def ecosystem_network(self) -> str:
        if self == Network.MAINNET:
            return "ethereum:mainnet"
        return "ethereum:hoodi"


@dataclass
class DeploymentResult:
    contract_address: str
    deployer_address: str
    network: Network
    tx_hash: str


class FactoryDeployerService:

    def __init__(self, network: Network, account: AccountAPI):
        self._network = network
        self._account = account

    def execute(self, publish: bool = False) -> DeploymentResult:
        ecosystem_network = self._network.ecosystem_network

        with networks.parse_network_choice(f"{ecosystem_network}:node"):
            factory = project.DelegationFactory.deploy(
                sender=self._account,
                publish=publish,
            )
            return DeploymentResult(
                contract_address=factory.address,
                deployer_address=self._account.address,
                network=self._network,
                tx_hash=factory.receipt.txn_hash,
            )
