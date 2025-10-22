#!/usr/bin/env python3
# Grant or revoke a delegate's permission for a specific target+selector.
# Usage examples:
#   .ape run scripts/xxx_grant_delegate.py \
#       --network ethereum:sepolia \
#       --contract <DEA_ADDRESS> \
#       --delegate <DELEGATE_ADDR> \
#       --target <TARGET_ADDR> \
#       --selector <0x12345678> \
#       --allowed true \
#       --expiry 0 \
#       --value-limit 0
#
# Compute selector helper: pass a function signature and the script will compute it.
#   --sig "transfer(address,uint256)"

from ape import accounts, Contract
import argparse
from eth_utils import keccak


def fn_selector_from_sig(sig: str) -> str:
    k = keccak(text=sig)
    return "0x" + k[:4].hex()


def main():
    parser = argparse.ArgumentParser(description="Grant/revoke delegate permission")
    parser.add_argument("--contract", required=True, help="DelegatedExecutionAuthority address")
    parser.add_argument("--delegate", required=True, help="Delegate (hot key) address")
    parser.add_argument("--target", required=True, help="Target contract address")
    parser.add_argument("--selector", help="4-byte selector in 0x-prefixed hex")
    parser.add_argument("--sig", help="Function signature, e.g. transfer(address,uint256)")
    parser.add_argument("--allowed", required=True, choices=["true", "false"], help="Allow or disallow")
    parser.add_argument("--expiry", type=int, default=0, help="Unix timestamp; 0 = no expiry")
    parser.add_argument("--value-limit", type=int, default=0, help="Max msg.value allowed; 0 = unlimited")
    args = parser.parse_args()

    if not args.selector and not args.sig:
        raise SystemExit("Provide either --selector or --sig")

    selector = args.selector
    if not selector and args.sig:
        selector = fn_selector_from_sig(args.sig)
        print(f"Computed selector from sig '{args.sig}': {selector}")

    # bytes4
    if len(selector) != 10:
        raise SystemExit("Selector must be 4 bytes (0x + 8 hex)")

    dea = Contract(args.contract)

    # pick owner account
    acct = accounts.load("default") if "default" in accounts.aliases else accounts.test_accounts[0]

    allowed = args.allowed.lower() == "true"

    print("Sending tx set_permission(...) ...")
    tx = dea.set_permission(args.delegate, args.target, selector, allowed, args.expiry, args.value_limit, sender=acct)
    print("Tx sent:", tx.txn_hash)
