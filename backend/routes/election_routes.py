"""
Election Management Routes (Person 3)
Enforces election lifecycle transitions on the Solidity smart contract.
"""

from fastapi import APIRouter, HTTPException, status
from backend.models.schemas import ElectionStartRequest
from backend.services.blockchain_service import blockchain_service
from backend.services.audit_service import audit_service

router = APIRouter(prefix="/api/election", tags=["Election"])


@router.get("/status")
def get_election_status():
    """Returns current on-chain election state and active election ID."""
    info = blockchain_service.get_election_status()
    network_info = blockchain_service.get_network_info()
    return {
        "status": info.get("status"),
        "election_id": info.get("election_id"),
        "blockchain_connected": network_info.get("connected"),
        "block_number": network_info.get("block_number"),
        "contract_address": network_info.get("contract_address"),
    }


@router.post("/start")
def start_election(payload: ElectionStartRequest):
    """Starts an election on the smart contract."""
    try:
        res = blockchain_service.start_election(payload.election_id)
        audit_service.log(
            event_type="ELECTION_STARTED",
            event_data={
                "election_id": payload.election_id,
                "transaction_hash": res["transaction_hash"],
                "block_number": res["block_number"],
            },
        )
        return {
            "success": True,
            "message": f"Election '{payload.election_id}' is now ACTIVE on blockchain.",
            "election_id": payload.election_id,
            "transaction_hash": res["transaction_hash"],
            "block_number": res["block_number"],
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to start election: {str(e)}",
        )


@router.post("/end")
def end_election():
    """Ends the currently active election on the smart contract."""
    try:
        res = blockchain_service.end_election()
        audit_service.log(
            event_type="ELECTION_ENDED",
            event_data={
                "transaction_hash": res["transaction_hash"],
                "block_number": res["block_number"],
            },
        )
        return {
            "success": True,
            "message": "Election has been marked ENDED on blockchain.",
            "transaction_hash": res["transaction_hash"],
            "block_number": res["block_number"],
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to end election: {str(e)}",
        )
