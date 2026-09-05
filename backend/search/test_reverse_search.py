#!/usr/bin/env python3
"""
CLI Test Script for Reverse Image Search Module (reverse_search.py)
Usage:
    python test_reverse_search.py                            # Run automated test suite
    python test_reverse_search.py --image path/to/photo.jpg  # Test custom image
"""

import argparse
import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw

# Ensure backend root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from search.reverse_search import reverse_image_search


def create_test_image(filename: str = "test_search_input.jpg") -> str:
    """Create a sample test image for CLI testing."""
    img = Image.new("RGB", (300, 300), color=(70, 130, 180))
    draw = ImageDraw.Draw(img)
    draw.ellipse([75, 75, 225, 225], fill=(255, 220, 185), outline=(200, 150, 120), width=3)
    path = Path(filename)
    img.save(path)
    return str(path)


def main():
    parser = argparse.ArgumentParser(description="CLI Test Script for Reverse Image Search Module")
    parser.add_argument("--image", type=str, help="Path to input image file to test")
    parser.add_argument("--url", type=str, help="Public image URL to test")
    parser.add_argument("--top-k", type=int, default=3, help="Number of top candidates to return")
    parser.add_argument("--social-only", action="store_true", help="Filter exclusively to social platforms")

    args = parser.parse_args()

    print("==================================================")
    print("Testing Reverse Image Search Engine (reverse_search.py)...")
    print("==================================================")

    if args.image or args.url:
        target_img = args.image
        target_url = args.url
        cleanup = False
    else:
        target_img = create_test_image()
        target_url = None
        cleanup = True

    try:
        result = reverse_image_search(
            image_input=target_img,
            image_url=target_url,
            filter_social_only=args.social_only,
            top_k=args.top_k,
        )

        print(f"\n[OK] Search Status: {result.status.upper()}")
        print(f" - Provider Engine Used: {result.provider_used}")
        print(f" - Total Matches Found: {result.total_matches_found}")
        print(f" - Social Platform Matches: {result.social_matches_count}")
        print(f" - Verified Matches Count: {result.verified_count}")
        print(f" - Top Candidates Returned: {len(result.candidates)}")

        if result.warnings:
            print("\n [WARN] Warnings:")
            for w in result.warnings:
                print(f"    - {w}")

        print("\n--- TOP RANKED MATCHING CANDIDATES ---")
        for idx, candidate in enumerate(result.candidates, start=1):
            social_tag = "[SOCIAL]" if candidate.is_social_platform else "[WEB]"
            verified_tag = "[VERIFIED MATCH]" if candidate.is_verified else "[UNVERIFIED]"
            print(f"\nCandidate #{idx} {social_tag} {verified_tag}:")
            print(f"  Title            : {candidate.title}")
            print(f"  URL              : {candidate.url}")
            print(f"  Source Domain    : {candidate.source_domain}")
            print(f"  Visual Relevance : {candidate.relevance_score:.2f}")
            print(f"  Facial Similarity: {candidate.facial_similarity_score * 100:.1f}% (Cosine Sim: {candidate.facial_similarity_score:.4f})")
            print(f"  Thumbnail        : {candidate.thumbnail}")


    finally:
        if cleanup and Path(target_img).exists():
            Path(target_img).unlink()

    print("\n[SUCCESS] Reverse search verification CLI test completed successfully!")



if __name__ == "__main__":
    main()
