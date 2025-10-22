# Call set code for EOA account
# Usage:
#   ape run set_code --wallet_address 0x01234 --contract_address 0x01234
#   or
#   poetry run python scripts/set_code.py --wallet_address 0x01234 --contract_address 0x01234

import sys

import click
from ape import accounts, Contract
from ape._cli import cli as ape_cli
from ape.cli import ConnectedProviderCommand


@click.command(cls=ConnectedProviderCommand)
@click.option("--wallet_address", type=str, required=True)
@click.option("--contract_address", type=str, required=True)
def cli(ecosystem, network, provider, wallet_address, contract_address):
    account = accounts.load("DEPLOYER")
    hot = accounts.load("HOT")

    # contract = Contract(contract_address)

    # contract.write(hot.address, to=account.address, sender=account)
    #
    # contract.delegate_1(to=account.address, sender=hot)


    # account.set_delegate(contract_address, gas_limit=300_000)
    # account.remove_delegate()
    #
    # sig = account.sign_authorization(contract.address)
    #
    # auth = Authorization.from_signature(
    #     address=contract.address,
    #     chain_id=network.chain_id,
    #     nonce=account.nonce,
    #     signature=sig,
    # )
    #
    # account.set_delegate(contract_address)
    #
    # contract.methodWith
    #
    # tx = {
    #     'type': 0x04,
    #     'chainId': network.chain_id,
    #     'from': wallet_address,
    #     'to': wallet_address,
    #     'nonce': provider.get_nonce(wallet_address),
    #     'maxFeePerGas': provider.web3.to_wei("30", "gwei"),
    #     'maxPriorityFeePerGas': provider.web3.to_wei("1", "gwei"),
    #     'gas': 300_000,
    #     'data': '',
    # }
    #
    # account = Account(wallet_address)
    #
    # sig = account.sign_authorization(contract)
    # auth = Authorization.from_signature(
    #     address=contract_address,
    #     chain_id=network.chain_id,
    #     nonce=account.nonce,
    #     signature=sig,
    # )
    #
    # click.echo(f"Verifying contract {address}...")
    # result = verify_contract(address)
    # click.echo(f"Verification result: {str(result)}")


if __name__ == "__main__":
    sys.argv = ['.ape', 'run', 'set_code', *sys.argv[1:]]
    ape_cli()
