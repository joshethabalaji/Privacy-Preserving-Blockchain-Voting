"""
Integration Routes (Person 3)
Provides mock integration endpoints for Person 1 (voter verification/lockout module)
and seed helpers for Person 2 encrypted ballot submissions.
"""

from typing import Dict, Any, List
from fastapi import APIRouter
from backend.models.schemas import Person1ConfirmationPayload
from backend.services.queue_service import queue_service
from backend.services.notification_service import notification_service

router = APIRouter(prefix="/api/integration", tags=["Integration Boundary"])

# In-memory record of received confirmations on Person 1's mock endpoint
person1_received_confirmations: List[Dict[str, Any]] = []


@router.post("/person1/vote-confirmed")
def receive_person1_confirmation(payload: Person1ConfirmationPayload):
    """
    Mock Person 1 endpoint that receives blockchain confirmation.
    In the final system, Person 1 uses this signal to set voter 'has_voted = TRUE'.
    Notice: Payload contains ZERO voter PII or biometric data.
    """
    record = payload.model_dump()
    person1_received_confirmations.append(record)
    return {
        "status": "acknowledged",
        "message": "Person 1 Mock: Blockchain confirmation received. Voter session marked has_voted = true.",
        "payload": record,
    }


@router.get("/person1/notifications")
def get_person1_notifications():
    """Returns list of notifications dispatched by Person 3 and received by Person 1."""
    return {
        "dispatched_by_person3": notification_service.get_notification_history(),
        "received_by_mock_person1": list(person1_received_confirmations),
    }


@router.post("/seed-dummy-queue")
def seed_dummy_ballots():
    """
    Seeds standard 4 dummy test ballots (ENC_BALLOT_001 to 004) into the queue.
    """
    dummy_ballots = [
        {"election_id": "ELECTION_2026", "encrypted_ballot": "ENC_BALLOT_001", "nullifier": "NULLIFIER_001"},
        {"election_id": "ELECTION_2026", "encrypted_ballot": "ENC_BALLOT_002", "nullifier": "NULLIFIER_002"},
        {"election_id": "ELECTION_2026", "encrypted_ballot": "ENC_BALLOT_003", "nullifier": "NULLIFIER_003"},
        {"election_id": "ELECTION_2026", "encrypted_ballot": "ENC_BALLOT_004", "nullifier": "NULLIFIER_004"},
    ]

    added = []
    for b in dummy_ballots:
        try:
            item = queue_service.add_ballot(b)
            added.append(item)
        except Exception:
            pass  # ignore if already queued

    return {
        "success": True,
        "message": f"Seeded {len(added)} dummy ballots into queue.",
        "queue_count": queue_service.get_count(),
        "seeded_ballots": added,
    }
