#!/usr/bin/env python3
"""
Usage:
    uv run python scripts/deploy_factory.py --network testnet
    uv run python scripts/deploy_factory.py --network mainnet --publish
"""

import argparse
import os

from ape_accounts import import_account_from_private_key

from services import FactoryDeployerService, Network


def main():
    """
    Args:
        --network: Target network (mainnet or testnet/hoodi)
        --publish: Verify and publish contract source on block explorer

    Env:
        DEPLOYER_PRIVATE_KEY: Private key for deployment

    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--network", choices=["mainnet", "testnet"], required=True)
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()

    private_key = os.environ["DEPLOYER_PRIVATE_KEY"]
    account = import_account_from_private_key("deployer", "", private_key)

    network = Network(args.network)
    result = FactoryDeployerService(network, account).execute(publish=args.publish)

    print(f"Contract deployed: {result.contract_address}")
    print(f"Transaction: {result.tx_hash}")


if __name__ == "__main__":
    main()
