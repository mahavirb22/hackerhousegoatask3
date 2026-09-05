import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from chain.ipfs_upload import (
    upload_matched_post_to_ipfs,
    compute_embedding_hash,
    compute_bytes32_data_hash,
    IPFSUploadResult,
)

__all__ = [
    "upload_matched_post_to_ipfs",
    "compute_embedding_hash",
    "compute_bytes32_data_hash",
    "IPFSUploadResult",
]
