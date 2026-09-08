"""
Vote Routes (Person 3)
Handles direct vote submission, validates nullifiers, records votes on-chain,
and dispatches notifications to Person 1 and Person 2 upon confirmation.
"""

from fastapi import APIRouter, HTTPException, status
from backend.models.schemas import VoteSubmissionRequest, Person2ReceiptResponse
from backend.services.blockchain_service import blockchain_service
from backend.services.audit_service import audit_service
from backend.services.notification_service import notification_service

router = APIRouter(prefix="/api", tags=["Vote"])


@router.post("/vote", response_model=Person2ReceiptResponse)
def submit_vote(payload: VoteSubmissionRequest):
    """
    Submits an individual protected encrypted ballot directly to the blockchain.
    Enforces on-chain election state and nullifier uniqueness.
    """
    election_id = payload.election_id
    nullifier = payload.nullifier
    encrypted_ballot = payload.encrypted_ballot
    batch_id = payload.batch_id or "BATCH_DIRECT"

    # 1. Verify election status
    status_info = blockchain_service.get_election_status()
    if status_info.get("status") != "ACTIVE":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot submit vote: Election status is {status_info.get('status')}. Must be ACTIVE.",
        )

    # 2. Check nullifier duplication on-chain
    if blockchain_service.is_nullifier_used(nullifier, election_id):
        audit_service.log(
            event_type="NULLIFIER_REJECTED",
            event_data={"election_id": election_id, "nullifier": nullifier, "reason": "Already used on blockchain"},
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vote rejected: nullifier has already been used.",
        )

    # 3. Submit transaction to Ganache and wait for confirmation receipt
    try:
        tx_result = blockchain_service.record_vote(nullifier, encrypted_ballot, batch_id)
        tx_hash = tx_result["transaction_hash"]
        block_num = tx_result["block_number"]

        # 4. Log to audit trail
        audit_service.log(
            event_type="VOTE_CONFIRMED",
            event_data={
                "election_id": election_id,
                "nullifier": nullifier,
                "batch_id": batch_id,
                "transaction_hash": tx_hash,
                "block_number": block_num,
            },
        )

        # 5. Notify Person 1 ONLY after blockchain confirmation
        notification_service.notify_person1_vote_confirmed(
            election_id=election_id,
            transaction_hash=tx_hash,
            block_number=block_num,
        )

        # 6. Return Person 2 receipt
        receipt = notification_service.build_person2_receipt(
            transaction_hash=tx_hash,
            block_number=block_num,
            batch_id=batch_id,
            nullifier=nullifier,
            success=True,
        )
        return receipt

    except Exception as e:
        error_msg = str(e)
        if "nullifier has already been used" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Vote rejected: nullifier has already been used.",
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Blockchain transaction failed. Vote was not confirmed. Details: {error_msg}",
        )
