#!/usr/bin/env python3
"""
CLI Test Script for Verification & Tamper Detection Demo
Usage:
    python chain/test_tamper_demo.py
"""

import json
import sys
from pathlib import Path

# Ensure backend root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from chain.web3_client import VerificationChainClient


def main():
    print("==================================================")
    print("Testing On-Chain Integrity & Tamper Detection Demo")
    print("==================================================")

    client = VerificationChainClient()
    sample_hash = "0xb32a3e3179c1a3f4087802040b22435534e0168f0a6c60e3fac7b94309cce8ac"

    # 1. Test Verification Endpoint (/api/verify/{record_id})
    print("\n--- Step 1: Testing Genuine Content Verification (/api/verify) ---")
    ver_res = client.verify_ipfs_content_integrity(sample_hash)
    
    print(f"[OK] Verification Check Result:")
    print(f" - Match Status     : {ver_res['match']} (Verified: {ver_res['verified']})")
    print(f" - On-Chain Hash    : {ver_res['on_chain_hash']}")
    print(f" - Recomputed Hash  : {ver_res['recomputed_hash']}")
    print(f" - IPFS CID         : {ver_res['ipfs_cid']}")
    print(f" - Submitter Wallet : {ver_res['submitter']}")
    print(f" - Summary Message  : {ver_res['message']}")

    assert ver_res['match'] == True
    assert ver_res['on_chain_hash'] == ver_res['recomputed_hash']

    # 2. Test Tamper Detection Demo Endpoint (/api/tamper-demo)
    print("\n--- Step 2: Testing Deliberate Byte Mutation Demo (/api/tamper-demo) ---")
    tamper_res = client.tamper_demo_simulation(sample_hash)

    print(f"[OK] Tamper Simulation Output:")
    print(f" - Match Status     : {tamper_res['match']} (Tamper Simulated: {tamper_res['tamper_simulated']})")
    print(f" - Original On-Chain Hash    : {tamper_res['original_on_chain_hash']}")
    print(f" - Tampered Recomputed Hash  : {tamper_res['tampered_recomputed_hash']}")
    print(f" - Mutation Details          : {tamper_res['mutation_details']}")
    print(f" - Alert Flag                : {tamper_res['diff_detected']}")
    print(f" - Message                   : {tamper_res['message']}")

    assert tamper_res['match'] == False
    assert tamper_res['original_on_chain_hash'] != tamper_res['tampered_recomputed_hash']

    print("\n[SUCCESS] On-chain verification and Tamper Detection Demo completed successfully!")


if __name__ == "__main__":
    main()
