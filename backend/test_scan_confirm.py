#!/usr/bin/env python3
"""
CLI Test Script for End-to-End Scan & Confirm Pipeline
Usage:
    python test_scan_confirm.py
"""

import time
import sys
from pathlib import Path
from PIL import Image, ImageDraw

# Ensure backend root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from scan_pipeline import create_scan_job, run_scan_pipeline_sync, execute_confirm_phase4, JOBS_STORE


def create_sample_face_image(filename: str = "scan_test_face.jpg") -> bytes:
    """Create a synthetic face image for scan testing."""
    img = Image.new("RGB", (400, 400), color=(240, 240, 245))
    draw = ImageDraw.Draw(img)
    draw.ellipse([100, 100, 300, 300], fill=(255, 220, 185), outline=(200, 150, 120), width=3)
    draw.ellipse([150, 160, 180, 180], fill=(50, 50, 50))
    draw.ellipse([220, 160, 250, 180], fill=(50, 50, 50))
    draw.arc([160, 220, 240, 260], start=0, end=180, fill=(180, 50, 50), width=4)
    
    import io
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def main():
    print("==================================================")
    print("Testing End-to-End Scan (Phase 1-3) & Confirm (Phase 4) Pipeline...")
    print("==================================================")

    image_bytes = create_sample_face_image()

    # 1. Create Scan Job
    print("\n--- Step 1: Creating & Initializing Scan Job ---")
    job = create_scan_job()
    print(f"[OK] Job Created: {job.job_id} | Status: {job.status}")

    # 2. Run Synchronous Pipeline Processing (Phases 1-3)
    print("\n--- Step 2: Processing Phases 1-3 (Face Detection -> Search -> Verification) ---")
    run_scan_pipeline_sync(job.job_id, image_bytes, social_only=False, top_k=3)

    polled_job = JOBS_STORE.get(job.job_id).to_dict()
    print(f"[OK] Job Finished Processing:")
    print(f" - Job Status      : {polled_job['status'].upper()}")
    print(f" - Progress Pct    : {polled_job['progress_pct']}%")
    print(f" - Message         : {polled_job['message']}")
    
    scan_results = polled_job.get("results", {})
    top_cands = scan_results.get("reverse_search", {}).get("top_candidates", [])
    print(f" - Candidates Found: {len(top_cands)}")
    for idx, c in enumerate(top_cands, 1):
        print(f"    Candidate #{idx}: {c['title']} | Score: {c['facial_similarity_score']*100:.1f}% | Verified: {c['is_verified']}")

    assert polled_job['status'] == 'completed'
    assert len(top_cands) > 0

    # 3. Confirm Selected Match (Phase 4)
    print("\n--- Step 3: Executing Phase 4 (Confirm Match -> IPFS + Blockchain) ---")
    selected_url = top_cands[0]['url']
    confirm_res = execute_confirm_phase4(job.job_id, candidate_url=selected_url)

    print(f"[OK] Phase 4 Confirmation Complete:")
    print(f" - Match URL       : {confirm_res['selected_match_url']}")
    print(f" - IPFS CID        : {confirm_res['ipfs_cid']}")
    print(f" - IPFS Gateway    : {confirm_res['ipfs_gateway_url']}")
    print(f" - Data Hash       : {confirm_res['data_hash']}")
    print(f" - Transaction Hash: {confirm_res['transaction_hash']}")
    print(f" - Polygonscan Link: {confirm_res['polygonscan_link']}")

    assert confirm_res['status'] == 'success'
    assert confirm_res['transaction_hash'].startswith("0x")
    assert "polygonscan.com" in confirm_res['polygonscan_link']

    print("\n[SUCCESS] End-to-End Scan & Confirm workflow tested successfully!")


if __name__ == "__main__":
    main()
