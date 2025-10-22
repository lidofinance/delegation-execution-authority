# Verify contract on Etherscan
# Usage:
#   .ape run verify --contract_address 0x01234
#   or
#   poetry run python scripts/verify.py --contract_address 0x01234

import sys

import click
from ape._cli import cli as ape_cli
from ape.cli import ConnectedProviderCommand

from utils.verification import verify_contract, check_verification


@click.command(cls=ConnectedProviderCommand)
@click.argument("address", type=str, required=True)
def cli(ecosystem, network, provider, address):
    click.echo(f"Verifying contract {address}...")
    result = verify_contract(address)
    click.echo(f"Verification result: {str(result)}")


if __name__ == "__main__":
    sys.argv = ['.ape', 'run', 'verify', *sys.argv[1:]]
    ape_cli()
