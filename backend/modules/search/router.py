from typing import Optional
from fastapi import APIRouter, File, UploadFile, Form, HTTPException
from pydantic import BaseModel
from core.config import settings
from search.reverse_search import reverse_image_search

router = APIRouter(prefix="/search", tags=["Search API"])


class SearchRequest(BaseModel):
    query: str
    num_results: int = 5


@router.get("/status")
def get_search_module_status():
    """
    Get status of SerpAPI & Reverse Image Search module.
    """
    is_configured = bool(settings.SERPAPI_KEY and settings.SERPAPI_KEY != "your_serpapi_key_here")
    return {
        "module": "search",
        "primary_provider": "SerpAPI (Google Lens)",
        "fallback_provider": "Google Vision WEB_DETECTION",
        "configured": is_configured,
        "status": "ready",
    }


@router.post("/query")
def execute_search(request: SearchRequest):
    """
    Execute search query via SerpAPI.
    """
    is_configured = bool(settings.SERPAPI_KEY and settings.SERPAPI_KEY != "your_serpapi_key_here")
    return {
        "query": request.query,
        "configured": is_configured,
        "results": [
            {
                "title": f"Result {i+1} for '{request.query}'",
                "link": f"https://example.com/search?q={request.query}&id={i+1}",
                "snippet": f"Demonstration snippet for result #{i+1} using SerpAPI search module."
            }
            for i in range(min(request.num_results, 10))
        ]
    }


@router.post("/reverse")
async def execute_reverse_search(
    file: Optional[UploadFile] = File(None),
    image_url: Optional[str] = Form(None),
    similarity_threshold: float = Form(0.65),
    social_only: bool = Form(False),
    top_k: int = Form(3)
):
    """
    Perform reverse image search using uploaded image file or public image URL.
    Verifies candidate matches against target face embedding using cosine similarity threshold.
    """
    image_bytes = None
    if file:
        image_bytes = await file.read()

    try:
        result = reverse_image_search(
            image_input=image_bytes,
            image_url=image_url,
            similarity_threshold=similarity_threshold,
            filter_social_only=social_only,
            top_k=top_k,
        )
        return result.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reverse image search failed: {str(e)}")


