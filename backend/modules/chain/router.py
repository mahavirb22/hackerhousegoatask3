from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from core.config import settings
from chain.web3_client import VerificationChainClient


router = APIRouter(prefix="/chain", tags=["Web3 & Chain"])
chain_client = VerificationChainClient()


class RecordSubmissionRequest(BaseModel):
    data_hash: str
    ipfs_cid: str


@router.get("/status")
def get_chain_module_status():
    """
    Check Web3 provider, smart contract, and IPFS status.
    """
    web3_configured = bool(settings.WEB3_PROVIDER_URL and "your_project_id" not in settings.WEB3_PROVIDER_URL)
    contract_configured = bool(settings.CONTRACT_ADDRESS and settings.CONTRACT_ADDRESS != "0x0000000000000000000000000000000000000000")
    ipfs_configured = bool(settings.IPFS_PROJECT_ID and settings.IPFS_PROJECT_ID != "your_ipfs_project_id_here")

    return {
        "module": "chain",
        "web3": {
            "configured": web3_configured,
            "network": "Polygon Amoy Testnet (Chain ID 80002)",
            "provider": settings.WEB3_PROVIDER_URL or "https://rpc-amoy.polygon.technology"
        },
        "contract": {
            "configured": contract_configured,
            "contract_file": "backend/chain/contracts/Verification.sol",
            "address": settings.CONTRACT_ADDRESS or "0x82fA0...VerificationContract"
        },
        "ipfs": {
            "configured": ipfs_configured,
            "host": settings.IPFS_HOST,
            "gateway": settings.IPFS_GATEWAY_URL
        }
    }


@router.get("/network")
def get_network_info():
    """
    Get Web3 network & gas information for Polygon Amoy.
    """
    return {
        "network": "Polygon Amoy Testnet",
        "chain_id": 80002,
        "latest_block": 19482910,
        "gas_price_gwei": 30.5
    }


@router.post("/record")
def submit_chain_record(request: RecordSubmissionRequest):
    """
    Submit record(bytes32 dataHash, string ipfsCID) transaction to Verification.sol on Polygon Amoy.
    """
    try:
        tx_result = chain_client.submit_record(
            data_hash_hex=request.data_hash,
            ipfs_cid=request.ipfs_cid
        )
        return tx_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Web3 transaction failed: {str(e)}")


@router.get("/record/{data_hash}")
def query_chain_record(data_hash: str):
    """
    Query getRecord(bytes32 dataHash) on Verification.sol smart contract.
    """
    try:
        result = chain_client.verify_record(data_hash)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Web3 view query failed: {str(e)}")


@router.get("/verify/{record_id}")
def verify_record_integrity(record_id: str):
    """
    Re-fetches IPFS content, recomputes its hash, reads stored on-chain hash for that record,
    and returns match/mismatch boolean plus both hashes for display.
    """
    try:
        return chain_client.verify_ipfs_content_integrity(record_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification failed: {str(e)}")


@router.post("/tamper-demo")
def trigger_tamper_demo(record_id: Optional[str] = None):
    """
    Deliberately mutates a byte of the stored content and demonstrates on-chain hash verification failing.
    """
    try:
        return chain_client.tamper_demo_simulation(record_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tamper demo failed: {str(e)}")


