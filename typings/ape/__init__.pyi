from contextlib import AbstractContextManager
from typing import Any

from ape.contracts import ContractContainer

class NetworkAPI:
    def use_provider(self, provider: str) -> AbstractContextManager[Any]: ...

class EthereumNetwork:
    mainnet_fork: NetworkAPI

class NetworkManager:
    ethereum: EthereumNetwork

class ProjectManager:
    DelegationFactory: ContractContainer
    DelegationContract: ContractContainer

class CompilerManager:
    def compile_source(
        self, compiler: str, source: str, contractName: str = ...
    ) -> ContractContainer: ...

project: ProjectManager
networks: NetworkManager
compilers: CompilerManager

def reverts(*args: Any, **kwargs: Any) -> AbstractContextManager[Any]: ...
