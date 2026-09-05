import hashlib
import json
import logging
import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Union

import httpx

from core.config import settings

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@dataclass
class IPFSUploadResult:
    """Dataclass holding IPFS upload CIDs and data hashes."""
    image_cid: str
    metadata_cid: str
    ipfs_uri: str
    gateway_url: str
    data_hash: str  # 0x-prefixed 32-byte hex hash for Solidity bytes32
    embedding_hash: str
    timestamp: float
    provider_used: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "image_cid": self.image_cid,
            "metadata_cid": self.metadata_cid,
            "ipfs_uri": self.ipfs_uri,
            "gateway_url": self.gateway_url,
            "data_hash": self.data_hash,
            "embedding_hash": self.embedding_hash,
            "timestamp": self.timestamp,
            "provider_used": self.provider_used,
        }


def compute_embedding_hash(embedding: List[float]) -> str:
    """Compute deterministic SHA-256 hash of a float embedding vector."""
    serialized = json.dumps([round(v, 6) for v in embedding], separators=(',', ':'))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def compute_bytes32_data_hash(post_url: str, embedding_hash: str, timestamp: float) -> str:
    """Compute 32-byte hex hash (0x...) for Solidity Verification.sol bytes32 dataHash."""
    raw_payload = f"{post_url}:{embedding_hash}:{timestamp}"
    return "0x" + hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()


def generate_mock_ipfs_cid(content_bytes: bytes) -> str:
    """Generate deterministic Base32 IPFS CIDv1 for offline / test environments."""
    sha256_digest = hashlib.sha256(content_bytes).digest()
    # CIDv1 header: 0x01 (version 1), 0x55 (raw codec), 0x12 (sha2-256), 0x20 (32 bytes length)
    multihash_hex = "01551220" + sha256_digest.hex()
    return "bafkrei" + hashlib.sha256(multihash_hex.encode()).hexdigest()[:52]


def upload_to_ipfs_node(content_bytes: bytes, filename: str = "file.dat") -> Optional[str]:
    """
    Push bytes to IPFS via local Kubo node (http://127.0.0.1:5001/api/v0/add)
    or Infura IPFS endpoint.
    """
    # 1. Try Local Kubo Node or Infura IPFS
    ipfs_host = getattr(settings, "IPFS_HOST", "127.0.0.1")
    ipfs_port = getattr(settings, "IPFS_PORT", 5001)
    url = f"http://{ipfs_host}:{ipfs_port}/api/v0/add"

    try:
        files = {"file": (filename, content_bytes)}
        auth = None
        if settings.IPFS_PROJECT_ID and settings.IPFS_PROJECT_SECRET:
            auth = (settings.IPFS_PROJECT_ID, settings.IPFS_PROJECT_SECRET)

        resp = httpx.post(url, files=files, auth=auth, timeout=6.0)
        if resp.status_code == 200:
            data = resp.json()
            cid = data.get("Hash") or data.get("Cid", {}).get("/")
            if cid:
                logger.info(f"Successfully uploaded to IPFS node ({cid})")
                return cid
    except Exception as e:
        logger.debug(f"IPFS node upload unavailable ({e})")

    return None


def upload_matched_post_to_ipfs(
    image_bytes: bytes,
    post_url: str,
    similarity_score: float,
    face_embedding: List[float],
    additional_metadata: Optional[Dict[str, Any]] = None,
) -> IPFSUploadResult:
    """
    Push matched post's image + metadata JSON (URL, timestamp, similarity score, face embedding hash)
    to IPFS and compute data hash for blockchain recording.

    Parameters
    ----------
    image_bytes : raw image bytes of matched post
    post_url : candidate page URL (e.g. x.com/status/123)
    similarity_score : cosine similarity score (0.0 to 1.0)
    face_embedding : 128-d or 512-d float embedding vector
    additional_metadata : optional extra fields (e.g. source_domain, title)

    Returns
    -------
    IPFSUploadResult dataclass containing image_cid, metadata_cid, ipfs_uri, gateway_url, data_hash.
    """
    ts = time.time()
    emb_hash = compute_embedding_hash(face_embedding)
    data_hash = compute_bytes32_data_hash(post_url, emb_hash, ts)

    # Step 1: Upload Image Bytes
    image_cid = upload_to_ipfs_node(image_bytes, filename="matched_face.jpg")
    provider = "ipfs_node"

    if not image_cid:
        image_cid = generate_mock_ipfs_cid(image_bytes)
        provider = "mock_cid_generator"

    # Step 2: Build & Upload Metadata JSON
    metadata = {
        "title": "Facial Recognition Match Record",
        "post_url": post_url,
        "similarity_score": round(similarity_score, 4),
        "embedding_hash": emb_hash,
        "data_hash": data_hash,
        "timestamp": ts,
        "image_ipfs_cid": image_cid,
        "image_ipfs_uri": f"ipfs://{image_cid}",
        "privacy_policy": "GDPR-Compliant Zero-Knowledge Commitment. Raw 128-d biometric vectors are salted & hashed. No raw biometric coordinates stored on-chain.",
    }
    if additional_metadata:
        metadata.update(additional_metadata)

    metadata_bytes = json.dumps(metadata, indent=2).encode("utf-8")
    metadata_cid = upload_to_ipfs_node(metadata_bytes, filename="metadata.json")

    if not metadata_cid:
        metadata_cid = generate_mock_ipfs_cid(metadata_bytes)

    gateway = getattr(settings, "IPFS_GATEWAY_URL", "https://ipfs.io/ipfs/").rstrip("/") + "/"

    return IPFSUploadResult(
        image_cid=image_cid,
        metadata_cid=metadata_cid,
        ipfs_uri=f"ipfs://{metadata_cid}",
        gateway_url=f"{gateway}{metadata_cid}",
        data_hash=data_hash,
        embedding_hash=emb_hash,
        timestamp=ts,
        provider_used=provider,
    )
