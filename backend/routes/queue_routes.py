"""
Queue Routes (Person 3)
Handles temporary ballot queueing, randomized shuffling, and batch blockchain submission.
"""

from fastapi import APIRouter, HTTPException, status
from backend.models.schemas import QueueAddRequest, ProcessQueueRequest
from backend.services.queue_service import queue_service
from backend.services.batch_service import batch_service
from backend.services.blockchain_service import blockchain_service

router = APIRouter(prefix="/api/queue", tags=["Queue"])


@router.post("/add")
def add_to_queue(payload: QueueAddRequest):
    """Adds an encrypted ballot to the temporary protected queue."""
    # Check election status
    status_info = blockchain_service.get_election_status()
    if status_info.get("status") != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot queue ballot: Election status is {status_info.get('status')}. Must be ACTIVE.",
        )

    # Check if nullifier is already used on chain
    if blockchain_service.is_nullifier_used(payload.nullifier, payload.election_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vote rejected: nullifier has already been used.",
        )

    try:
        item = queue_service.add_ballot(payload.model_dump())
        return {
            "success": True,
            "message": "Ballot added to protected queue",
            "queue_count": queue_service.get_count(),
            "item": item,
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("")
def get_queue():
    """Returns all ballots currently in the temporary queue."""
    return {
        "count": queue_service.get_count(),
        "queue": queue_service.get_queue(),
    }


@router.post("/shuffle")
def shuffle_queue():
    """Cryptographically shuffles the current queue order."""
    shuffled = batch_service.shuffle_current_queue()
    return {
        "success": True,
        "message": "Queue order randomized using cryptographic entropy source.",
        "count": len(shuffled),
        "queue": shuffled,
    }


@router.post("/process")
def process_queue(payload: ProcessQueueRequest = ProcessQueueRequest()):
    """
    Shuffles queued ballots, creates a batch, submits to Ganache,
    verifies confirmation, and dispatches callbacks.
    """
    if queue_service.get_count() == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Queue is empty. Please add ballots to the queue before processing.",
        )

    try:
        result = batch_service.process_queue(
            batch_id=payload.batch_id, max_batch_size=payload.max_batch_size or 10
        )
        return result
    except Exception as e:
        error_msg = str(e)
        if "nullifier" in error_msg and "already been used" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vote rejected: nullifier has already been used.",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch processing failed: {error_msg}",
        )


@router.delete("")
def clear_queue():
    """Clears all ballots from the temporary queue."""
    queue_service.clear()
    return {"success": True, "message": "Ballot queue cleared."}
