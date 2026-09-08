"""
Automated Privacy & Boundary Isolation Tests (Person 3).
Verifies that NO voter personally identifiable information (PII) or plaintext candidate data
can enter or exist in Person 3 data stores, logs, or smart contract records.
"""

import pytest
from backend.services.queue_service import queue_service
from backend.services.audit_service import audit_service
from backend.services.blockchain_service import blockchain_service

FORBIDDEN_PII_KEYS = [
    "voter_id", "voterid", "name", "voter_name", "address", "age",
    "iris", "iris_template", "iris_image", "biometric", "phone",
    "email", "password", "temporary_authorization", "auth_token",
    "candidate", "candidate_name", "candidate_id"
]


def test_api_rejects_pii_in_vote_payload(client):
    """Ensures POST /api/vote forbids extra/PII attributes."""
    payload_with_voter_id = {
        "election_id": "ELECTION_2026",
        "encrypted_ballot": "ENC_BALLOT_001",
        "nullifier": "NULLIFIER_PRIVACY_01",
        "voter_id": "VOTER_SECRET_12345",  # FORBIDDEN
    }
    res = client.post("/api/vote", json=payload_with_voter_id)
    # Pydantic extra='forbid' returns 422
    assert res.status_code == 422


def test_api_rejects_iris_in_queue_payload(client):
    """Ensures POST /api/queue/add forbids biometric attributes."""
    payload_with_iris = {
        "election_id": "ELECTION_2026",
        "encrypted_ballot": "ENC_BALLOT_001",
        "nullifier": "NULLIFIER_PRIVACY_02",
        "iris_template": "BASE64_BIOMETRIC_DATA_XYZ",  # FORBIDDEN
    }
    res = client.post("/api/queue/add", json=payload_with_iris)
    assert res.status_code == 422


def test_audit_log_contains_zero_pii():
    """Scans all historical audit log entries to ensure zero PII leaks."""
    chain = audit_service.get_chain()
    for entry in chain:
        event_data = entry.get("event_data", {})
        for k in event_data.keys():
            assert k.lower() not in FORBIDDEN_PII_KEYS, f"PII key '{k}' leaked into audit log entry {entry['index']}"


def test_queue_contains_zero_pii():
    """Scans all queued items to ensure zero PII fields."""
    items = queue_service.get_queue()
    for item in items:
        for k in item.keys():
            assert k.lower() not in FORBIDDEN_PII_KEYS, f"PII key '{k}' leaked into queue item"


def test_blockchain_records_contain_zero_pii():
    """Scans on-chain records returned from contract to ensure zero PII."""
    records = blockchain_service.get_vote_records()
    for record in records:
        for k in record.keys():
            assert k.lower() not in FORBIDDEN_PII_KEYS, f"PII key '{k}' found in blockchain record"
