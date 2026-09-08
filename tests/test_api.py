"""
API Endpoint Integration Tests (Person 3).
Validates end-to-end HTTP API responses for election control, ballot queueing,
blockchain audit querying, audit verification, and inter-module boundaries.
"""

import pytest


def test_health_check_endpoint(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["service"] == "person3-blockchain-voting"


def test_election_lifecycle_endpoints(client, deployed_contract):
    # Check initial status
    res_status = client.get("/api/election/status")
    if res_status.json().get("status") != "ACTIVE":
        res_start = client.post("/api/election/start", json={"election_id": "ELECTION_API_TEST"})
        assert res_start.status_code == 200
        assert res_start.json()["success"] is True

    # Check Status
    res_status = client.get("/api/election/status")
    assert res_status.status_code == 200
    assert res_status.json()["status"] == "ACTIVE"


def test_queue_and_batch_endpoints(client):
    # Ensure active election
    res_status = client.get("/api/election/status")
    if res_status.json().get("status") != "ACTIVE":
        client.post("/api/election/start", json={"election_id": "ELECTION_API_TEST"})

    # 1. Seed Queue
    res_seed = client.post("/api/integration/seed-dummy-queue")
    assert res_seed.status_code == 200
    assert res_seed.json()["queue_count"] >= 4

    # 2. Get Queue
    res_queue = client.get("/api/queue")
    assert res_queue.status_code == 200
    assert res_queue.json()["count"] >= 4

    # 3. Shuffle Queue
    res_shuffle = client.post("/api/queue/shuffle")
    assert res_shuffle.status_code == 200
    assert res_shuffle.json()["success"] is True

    # 4. Process Batch
    res_proc = client.post("/api/queue/process", json={"max_batch_size": 10})
    assert res_proc.status_code == 200
    data = res_proc.json()
    assert data["success"] is True
    assert "transaction_hash" in data
    assert data["person1_notified"] is True


def test_duplicate_nullifier_rejection_via_api(client):
    # Attempting to submit a vote with already processed NULLIFIER_001
    res = client.post("/api/vote", json={
        "election_id": "ELECTION_API_TEST",
        "encrypted_ballot": "ENC_BALLOT_REPLAY_ATTEMPT",
        "nullifier": "NULLIFIER_001",
    })
    assert res.status_code == 400
    assert "nullifier has already been used" in res.json()["detail"]


def test_audit_endpoints(client):
    # 1. Get Audit Trail
    res_audit = client.get("/api/audit")
    assert res_audit.status_code == 200
    assert res_audit.json()["count"] > 1

    # 2. Verify Audit Chain
    res_verify = client.get("/api/audit/verify")
    assert res_verify.status_code == 200
    assert res_verify.json()["verified"] is True

    # 3. Tamper Demo
    res_tamper = client.post("/api/audit/tamper-demo")
    assert res_tamper.status_code == 200
    assert res_tamper.json()["success"] is True
    assert res_tamper.json()["after_tampering"]["verification"]["verified"] is False


def test_blockchain_audit_and_results_endpoints(client):
    res_audit = client.get("/api/blockchain/audit")
    assert res_audit.status_code == 200
    assert res_audit.json()["total_votes_on_chain"] > 0

    res_results = client.get("/api/results")
    assert res_results.status_code == 200
    assert "SIMULATED TALLY" in res_results.json()["disclaimer"]
    assert res_results.json()["total_votes"] > 0


def test_person1_callback_endpoint(client):
    payload = {
        "vote_recorded": True,
        "election_id": "ELECTION_API_TEST",
        "transaction_hash": "0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
        "block_number": 42,
    }
    res = client.post("/api/integration/person1/vote-confirmed", json=payload)
    assert res.status_code == 200
    assert res.json()["status"] == "acknowledged"
