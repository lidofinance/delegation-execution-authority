# Deploy the DelegationManager contract.
# Usage:
#   .ape run deploy --network ethereum:hoodi
#   or
#   poetry run python scripts/deploy.py --network ethereum:hoodi-fork:foundry

import sys
import time

import click
from ape import accounts, project
from ape._cli import cli as ape_cli

from ape.cli import ConnectedProviderCommand

from utils.verification import verify_contract, check_verification


@click.command(cls=ConnectedProviderCommand)
def cli(ecosystem, network, provider):
    click.echo(f"Connected to {ecosystem.name}:{network.name} using provider '{provider.name}'.")

    if network.name.endswith("-fork"):
        click.echo('Deploying on fork.')
        account = accounts.test_accounts[0]
    else:
        if "DEPLOYER" not in accounts.aliases:
            click.echo(f'To deploy on fork, use `ethereum:hoodi-fork:foundry` network.')
            click.echo(click.style("No account tagged 'DEPLOYER' found. Use `.ape accounts import DEPLOYER` to setup account.", fg="red"))
            sys.exit(1)

        account = accounts.load("DEPLOYER")

    click.echo("Deploying contract...")

    contract = account.deploy(project.DelegationManager)
    project.deployments.track(contract)

    click.echo("Try verification on Etherscan.")


if __name__ == "__main__":
    sys.argv = ['.ape', 'run', 'deploy', *sys.argv[1:]]
    ape_cli()
