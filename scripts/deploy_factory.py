#!/usr/bin/env python3
"""
Deploy DelegationFactory contract.

Usage:
    uv run ape run deploy_factory --network ethereum:mainnet:node
    uv run ape run deploy_factory --network ethereum:hoodi:node --publish
"""

import os

import click
from ape.cli import ConnectedProviderCommand, network_option
from ape_accounts import import_account_from_private_key

from services import FactoryDeployerService

DEPLOYER_ALIAS = "deployer"
DEPLOYER_PASSPHRASE = "deploy"


@click.command(cls=ConnectedProviderCommand)
@network_option(required=True)
@click.option(
    "--publish", is_flag=True, help="Verify and publish contract source on block explorer"
)
def cli(publish):
    private_key = os.environ.get("DEPLOYER_PRIVATE_KEY")
    if not private_key:
        raise click.ClickException("DEPLOYER_PRIVATE_KEY environment variable is required")

    account = import_account_from_private_key(DEPLOYER_ALIAS, DEPLOYER_PASSPHRASE, private_key)
    account.set_autosign(True, DEPLOYER_PASSPHRASE)

    result = FactoryDeployerService(account).execute(publish=publish)

    click.echo(f"Contract deployed: {result.contract.address}")
    click.echo(f"Transaction: {result.tx_hash}")
