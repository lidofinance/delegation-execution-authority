import os
import subprocess
import time

import requests

from ape import Contract, project
from ape.types.address import AddressType


def verify_contract(contract_address: AddressType) -> tuple[str, dict]:
    contract = Contract(contract_address)

    for compiler in project.manifest.compilers:
        if contract.contract_type.name in compiler.contractTypes:
            break
    else:
        raise Exception("Contract not found in project manifest.")

    constructor_calldata = contract.creation_metadata.receipt.data[len(contract.contract_type.deployment_bytecode.bytecode[2:])//2:]

    vyper_json = subprocess.run(["vyper", "-f", "solc_json", contract.contract_type.source_id], capture_output=True, text=True, check=True).stdout

    guid = submit_verification(
        source_code=vyper_json,
        constructor_arguments=constructor_calldata.hex(),
        contract_address=contract_address,
        contract_name=contract.contract_type.source_id.split('/')[-1] + ':' + contract.contract_type.name,
        compiler_version=compiler.version,
        optimization=True,  # ToDo fix this
        chain_id=contract.creation_metadata.chain_manager.chain_id,
    )
    time.sleep(5)
    return guid, check_verification(guid, contract.creation_metadata.chain_manager.chain_id)


def submit_verification(
    source_code: str,
    constructor_arguments: str,
    contract_address: str,
    contract_name: str,
    compiler_version: str,
    optimization: bool,
    chain_id: int,
) -> str:
    payload = {
        'codeformat': 'vyper-json',
        'sourceCode': source_code,
        'constructorArguments': constructor_arguments,
        'contractaddress': contract_address,
        'contractname': contract_name,
        'compilerversion': 'vyper:' + compiler_version,
        'optimizationUsed': 1 if optimization else 0,
    }

    api_key = os.environ['ETHERSCAN_API_KEY']

    response = requests.post(
        f'https://api.etherscan.io/v2/api?chainid={chain_id}&module=contract&action=verifysourcecode&apikey={api_key}',
        data=payload,
        timeout=10,
    )

    response.raise_for_status()
    return response.json()['result']


def check_verification(guid: str, chain_id: int) -> dict:
    api_key = os.environ['ETHERSCAN_API_KEY']

    response = requests.get(
        f'https://api.etherscan.io/v2/api?chainid={chain_id}&module=contract&action=checkverifystatus&guid={guid}&apikey={api_key}',
        timeout=10,
    )
    response.raise_for_status()
    return response.json()