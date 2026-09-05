from fastapi import APIRouter
from modules.face.router import router as face_router
from modules.search.router import router as search_router
from modules.chain.router import router as chain_router

api_router = APIRouter()

# Register sub-module routers
api_router.include_router(face_router)
api_router.include_router(search_router)
api_router.include_router(chain_router)


@api_router.get("/health", tags=["System"])
def api_health():
    """
    API v1 health status endpoint.
    """
    return {
        "status": "healthy",
        "service": "FastAPI Monorepo API v1",
        "modules_active": ["face", "search", "chain", "api"]
    }
