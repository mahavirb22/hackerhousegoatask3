import sys
from pathlib import Path

# Add backend directory to sys.path if not present
backend_dir = Path(__file__).resolve().parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from face.encode import (
    encode_face,
    FaceEncodingResult,
    FaceProcessingError,
    NoFaceDetectedError,
    LowQualityImageError,
    load_image,
    evaluate_image_quality,
    crop_face_thumbnail,
)

__all__ = [
    "encode_face",
    "FaceEncodingResult",
    "FaceProcessingError",
    "NoFaceDetectedError",
    "LowQualityImageError",
    "load_image",
    "evaluate_image_quality",
    "crop_face_thumbnail",
]
