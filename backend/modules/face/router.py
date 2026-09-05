import base64
from typing import Optional, List
from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from pydantic import BaseModel
from face.encode import (
    encode_face,
    NoFaceDetectedError,
    LowQualityImageError,
    FaceProcessingError
)

router = APIRouter(prefix="/face", tags=["Face Processing"])


class FaceAnalysisResponse(BaseModel):
    status: str
    faces_detected: int
    bounding_box: Optional[dict] = None
    embedding_dim: int
    embedding_sample: List[float]
    warnings: List[str]
    quality_score: float
    detector_used: str
    thumbnail_base64: Optional[str] = None
    message: str


@router.get("/status")
def get_face_module_status():
    """
    Get status of the Face Processing module.
    """
    return {
        "module": "face",
        "status": "ready",
        "engine": "dlib / OpenCV / Skin-Contour Face Encoder",
        "encode_file": "backend/face/encode.py",
    }


@router.post("/analyze", response_model=FaceAnalysisResponse)
async def analyze_face(
    file: Optional[UploadFile] = File(None),
    strict: bool = Form(False)
):
    """
    Upload an image to detect faces, extract largest face embedding (128-d),
    and generate thumbnail.
    """
    if file:
        image_bytes = await file.read()
    else:
        # Default demo synthetic image
        from PIL import Image, ImageDraw
        import io
        img = Image.new("RGB", (400, 400), color=(240, 240, 245))
        draw = ImageDraw.Draw(img)
        draw.ellipse([100, 100, 300, 300], fill=(255, 220, 185), outline=(200, 150, 120), width=3)
        draw.ellipse([150, 160, 180, 180], fill=(50, 50, 50))
        draw.ellipse([220, 160, 250, 180], fill=(50, 50, 50))
        draw.arc([160, 220, 240, 260], start=0, end=180, fill=(180, 50, 50), width=4)
        
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        image_bytes = buf.getvalue()

    try:
        result = encode_face(image_bytes, strict_quality=strict)
        
        # Convert thumbnail bytes to base64 string
        thumb_b64 = base64.b64encode(result.thumbnail_bytes).decode("utf-8")

        return FaceAnalysisResponse(
            status="success",
            faces_detected=result.face_count,
            bounding_box={
                "top": result.bounding_box[0],
                "right": result.bounding_box[1],
                "bottom": result.bounding_box[2],
                "left": result.bounding_box[3],
            },
            embedding_dim=len(result.embedding),
            embedding_sample=[round(v, 4) for v in result.embedding[:5]],
            warnings=result.warnings,
            quality_score=round(result.quality_score, 2),
            detector_used=result.detector_used,
            thumbnail_base64=f"data:image/jpeg;base64,{thumb_b64}",
            message="Face successfully processed.",
        )
    except NoFaceDetectedError as e:
        raise HTTPException(status_code=400, detail=f"No face detected: {str(e)}")
    except LowQualityImageError as e:
        raise HTTPException(status_code=422, detail=f"Low quality image: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Face processing error: {str(e)}")

