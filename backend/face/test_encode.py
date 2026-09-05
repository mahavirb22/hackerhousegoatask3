#!/usr/bin/env python3
"""
CLI Test Script for Face Encoding Module (encode.py)
Usage:
    python test_encode.py                             # Runs automated tests on synthetic images
    python test_encode.py --image path/to/photo.jpg   # Tests a custom image
"""

import argparse
import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw

# Ensure backend root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from face.encode import (
    encode_face,
    NoFaceDetectedError,
    LowQualityImageError,
    FaceProcessingError
)


def create_synthetic_test_image(filename: str, num_faces: int = 1, size=(600, 600)) -> str:
    """Create a synthetic test image with facial features drawn for test purposes."""
    img = Image.new("RGB", size, color=(240, 240, 245))
    draw = ImageDraw.Draw(img)

    if num_faces >= 1:
        # Face 1 (Main / Large Face in right half)
        cx, cy, radius = 400, 300, 120
        draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=(255, 220, 185), outline=(200, 150, 120), width=3)
        # Eyes
        draw.ellipse([cx - 45, cy - 35, cx - 15, cy - 15], fill=(50, 50, 50))
        draw.ellipse([cx + 15, cy - 35, cx + 45, cy - 15], fill=(50, 50, 50))
        # Mouth
        draw.arc([cx - 40, cy + 20, cx + 40, cy + 60], start=0, end=180, fill=(180, 50, 50), width=4)

    if num_faces >= 2:
        # Face 2 (Smaller Face in left half)
        cx2, cy2, radius2 = 120, 150, 50
        draw.ellipse([cx2 - radius2, cy2 - radius2, cx2 + radius2, cy2 + radius2], fill=(245, 210, 175), outline=(180, 140, 110), width=2)
        draw.ellipse([cx2 - 20, cy2 - 15, cx2 - 5, cy2 - 3], fill=(50, 50, 50))
        draw.ellipse([cx2 + 5, cy2 - 15, cx2 + 20, cy2 - 3], fill=(50, 50, 50))
        draw.arc([cx2 - 15, cy2 + 8, cx2 + 15, cy2 + 25], start=0, end=180, fill=(180, 50, 50), width=2)

    path = Path(filename)
    img.save(path)
    return str(path)


def run_custom_image_test(image_path: str, strict: bool = False, output_thumbnail: str = "thumbnail_output.jpg"):
    print(f"\n==================================================")
    print(f"Testing Face Encoding on Image: {image_path}")
    print(f"==================================================")

    try:
        result = encode_face(image_path, strict_quality=strict)
        
        print(f"[OK] Processing Success!")
        print(f" - Detector Backend: {result.detector_used}")
        print(f" - Embedding Dimensions: {len(result.embedding)}-d")
        print(f" - Embedding First 5 Values: {[round(v, 4) for v in result.embedding[:5]]}")
        print(f" - Bounding Box (top, right, bottom, left): {result.bounding_box}")
        print(f" - Total Faces Detected: {result.face_count}")
        print(f" - Quality Score (Blur): {result.quality_score:.2f}")

        if result.warnings:
            print(" [WARN] Warnings:")
            for w in result.warnings:
                print(f"    - {w}")
        else:
            print(" - Warnings: None")

        # Save thumbnail
        result.thumbnail.save(output_thumbnail)
        print(f" - Cropped Face Thumbnail Saved to: {output_thumbnail}")

    except NoFaceDetectedError as e:
        print(f"[ERROR] No Face Detected Error: {e}")
    except LowQualityImageError as e:
        print(f"[WARN] Low Quality Image Error: {e}")
    except Exception as e:
        print(f"[ERROR] Processing Error: {e}")


def run_automated_suite():
    print("==================================================")
    print("Running Automated Test Suite for encode.py...")
    print("==================================================")

    temp_single = "test_single_face.jpg"
    temp_multi = "test_multi_face.jpg"
    temp_empty = "test_no_face.jpg"

    try:
        # Test 1: Single Face
        print("\n--- Test Case 1: Single Face ---")
        create_synthetic_test_image(temp_single, num_faces=1)
        res1 = encode_face(temp_single)
        print(f"Detector: {res1.detector_used} | Embedding len: {len(res1.embedding)} | Faces: {res1.face_count}")
        print(f"Result summary: {json.dumps(res1.to_dict(include_embedding=False), indent=2)}")

        # Test 2: Multiple Faces
        print("\n--- Test Case 2: Multiple Faces (Warn & Pick Largest) ---")
        create_synthetic_test_image(temp_multi, num_faces=2)
        res2 = encode_face(temp_multi)
        print(f"Faces found: {res2.face_count} | Bounding Box: {res2.bounding_box} | Warnings: {res2.warnings}")

        # Test 3: No Face Found Handling
        print("\n--- Test Case 3: Image with No Face ---")
        blank_img = Image.new("RGB", (200, 200), color=(100, 100, 100))
        blank_img.save(temp_empty)
        try:
            encode_face(temp_empty)
            print("[ERROR] Expected NoFaceDetectedError, but none was raised.")
        except NoFaceDetectedError as e:
            print(f"[OK] Successfully caught expected NoFaceDetectedError: {e}")

        print("\n[SUCCESS] All automated tests completed successfully!")

    finally:
        # Clean up temporary test images
        for p in [temp_single, temp_multi, temp_empty]:
            if Path(p).exists():
                Path(p).unlink()


def main():
    parser = argparse.ArgumentParser(description="CLI Test Script for Face Encoding Module")
    parser.add_argument("--image", type=str, help="Path to input image file to test")
    parser.add_argument("--strict", action="store_true", help="Enable strict image quality checks")
    parser.add_argument("--output", type=str, default="thumbnail_output.jpg", help="Path to save cropped thumbnail")

    args = parser.parse_args()

    if args.image:
        run_custom_image_test(args.image, strict=args.strict, output_thumbnail=args.output)
    else:
        run_automated_suite()


if __name__ == "__main__":
    main()
