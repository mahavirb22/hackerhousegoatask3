import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from search.reverse_search import (
    reverse_image_search,
    ReverseSearchResult,
    ReverseSearchCandidate,
    upload_image_to_temp_host,
    KNOWN_SOCIAL_DOMAINS,
)

__all__ = [
    "reverse_image_search",
    "ReverseSearchResult",
    "ReverseSearchCandidate",
    "upload_image_to_temp_host",
    "KNOWN_SOCIAL_DOMAINS",
]
