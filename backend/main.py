import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from modules.api.router import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration allowing frontend connection
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Direct root /api/ alias routes for convenience
from typing import Optional
from fastapi import File, UploadFile, Form, BackgroundTasks, HTTPException
from pydantic import BaseModel
from chain.web3_client import VerificationChainClient
from scan_pipeline import (
    create_scan_job,
    run_scan_pipeline_sync,
    execute_confirm_phase4,
    JOBS_STORE,
)

chain_client = VerificationChainClient()


class ConfirmMatchRequest(BaseModel):
    job_id: str
    candidate_url: Optional[str] = None
    candidate_index: int = 0


@app.post("/api/scan", tags=["Scan & Confirm Pipeline"])
@app.post(f"{settings.API_V1_STR}/scan", tags=["Scan & Confirm Pipeline"])
async def start_scan_job(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    social_only: bool = Form(False),
    similarity_threshold: float = Form(0.65),
    top_k: int = Form(3)
):
    """
    Start asynchronous Scan Job executing Phases 1–3:
      - Phase 1: Face detection & embedding extraction
      - Phase 2: Reverse image search (Google Lens / Vision / Fallback)
      - Phase 3: Cosine similarity verification & social platform filtering
    Returns job_id and progress status URL for frontend polling.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="Invalid upload: Image file is required.")

    image_bytes = await file.read()
    if len(image_bytes) < 100:
        raise HTTPException(status_code=400, detail="Invalid image file: File is empty or corrupted.")

    job = create_scan_job()

    # Launch pipeline processing in background task
    background_tasks.add_task(
        run_scan_pipeline_sync,
        job_id=job.job_id,
        image_bytes=image_bytes,
        social_only=social_only,
        similarity_threshold=similarity_threshold,
        top_k=top_k,
    )

    return {
        "status": "processing",
        "job_id": job.job_id,
        "progress_pct": job.progress_pct,
        "message": job.message,
        "status_url": f"/api/scan/status/{job.job_id}",
    }


@app.get("/api/scan/status/{job_id}", tags=["Scan & Confirm Pipeline"])
@app.get(f"{settings.API_V1_STR}/scan/status/{{job_id}}", tags=["Scan & Confirm Pipeline"])
def get_scan_job_status(job_id: str):
    """
    Poll job progress status (processing_face -> searching_matches -> verifying_similarity -> completed / failed).
    """
    job = JOBS_STORE.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Scan Job '{job_id}' not found.")
    return job.to_dict()


@app.post("/api/confirm", tags=["Scan & Confirm Pipeline"])
@app.post(f"{settings.API_V1_STR}/confirm", tags=["Scan & Confirm Pipeline"])
def confirm_match_selection(request: ConfirmMatchRequest):
    """
    Execute Phase 4 for user-selected match candidate:
      - Pushes matched post image + metadata JSON to IPFS
      - Submits transaction to Verification.sol contract on Polygon Amoy
      - Returns tx_hash, IPFS CID, and direct Polygonscan link.
    """
    try:
        result = execute_confirm_phase4(
            job_id=request.job_id,
            candidate_url=request.candidate_url,
            candidate_index=request.candidate_index
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Phase 4 confirmation failed: {str(e)}")


@app.get("/api/verify/{record_id}", tags=["Verification & Tamper Demo"])
def root_verify_record(record_id: str):
    """
    Re-fetches IPFS content, recomputes its hash, reads on-chain hash, and returns match/mismatch boolean.
    """
    return chain_client.verify_ipfs_content_integrity(record_id)


@app.post("/api/tamper-demo", tags=["Verification & Tamper Demo"])
def root_tamper_demo(record_id: str = None):
    """
    Deliberately mutates a byte of stored content and proves on-chain hash verification failing.
    """
    return chain_client.tamper_demo_simulation(record_id)


@app.get("/", tags=["System"])
def root():
    return {
        "message": "Welcome to FastAPI Monorepo Service API",
        "docs": "/docs",
        "health": f"{settings.API_V1_STR}/health"
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


