#!/usr/bin/env python3
"""
CLI Test Script for Web3 & IPFS Chain Verification System
Usage:
    python chain/test_chain.py
"""

import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw

# Ensure backend root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from chain.ipfs_upload import upload_matched_post_to_ipfs
from chain.web3_client import VerificationChainClient


def main():
    print("==================================================")
    print("Testing Web3 & IPFS Chain Verification Pipeline...")
    print("==================================================")

    # 1. Create test synthetic image
    img = Image.new("RGB", (200, 200), color=(100, 150, 200))
    draw = ImageDraw.Draw(img)
    draw.ellipse([50, 50, 150, 150], fill=(255, 220, 185))
    
    import io
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    image_bytes = buf.getvalue()

    mock_embedding = [0.1234, -0.5678, 0.9876, 0.4321] + [0.0] * 124
    test_post_url = "https://x.com/verified_user/status/19827364"

    # 2. Push Image + Metadata to IPFS
    print("\n--- Step 1: Uploading Matched Image & Metadata to IPFS ---")
    ipfs_result = upload_matched_post_to_ipfs(
        image_bytes=image_bytes,
        post_url=test_post_url,
        similarity_score=0.965,
        face_embedding=mock_embedding,
        additional_metadata={"source_platform": "x.com", "verified_by": "FastAPI AI Engine"}
    )

    print(f"[OK] IPFS Upload Complete ({ipfs_result.provider_used}):")
    print(f" - Image CID   : {ipfs_result.image_cid}")
    print(f" - Metadata CID: {ipfs_result.metadata_cid}")
    print(f" - IPFS URI    : {ipfs_result.ipfs_uri}")
    print(f" - Gateway URL : {ipfs_result.gateway_url}")
    print(f" - Data Hash   : {ipfs_result.data_hash}")

    # 3. Submit Record to Web3 Contract
    print("\n--- Step 2: Submitting Record to Verification.sol Contract ---")
    client = VerificationChainClient()
    tx_result = client.submit_record(
        data_hash_hex=ipfs_result.data_hash,
        ipfs_cid=ipfs_result.metadata_cid
    )

    print(f"[OK] Web3 Transaction Submitted ({tx_result['mode']}):")
    print(f" - Transaction Hash : {tx_result['transaction_hash']}")
    print(f" - Contract Address : {tx_result['contract_address']}")
    print(f" - Submitter Wallet  : {tx_result['submitter']}")
    print(f" - Block Number     : {tx_result['block_number']}")

    # 4. Verify Record on Chain
    print("\n--- Step 3: Querying On-Chain Record (verify_record) ---")
    verification_check = client.verify_record(ipfs_result.data_hash)

    print(f"[OK] On-Chain Record Query Complete:")
    print(f" - Record Exists on Chain : {verification_check['exists']}")
    print(f" - Verified IPFS CID      : {verification_check['ipfs_cid']}")
    print(f" - Record Submitter       : {verification_check['submitter']}")
    print(f" - Block Timestamp        : {verification_check['timestamp']}")

    assert verification_check['exists'] == True
    assert verification_check['ipfs_cid'] == ipfs_result.metadata_cid

    print("\n[SUCCESS] Web3 & IPFS Chain verification test completed successfully!")


if __name__ == "__main__":
    main()
