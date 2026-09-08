"""
Unit tests for BallotQueue and BatchManager (Person 3).
"""

import pytest
try:
    from ballot_queue import BallotQueue, PrivacyViolationError
    from batch_manager import BatchManager
except ImportError:
    from queue.ballot_queue import BallotQueue, PrivacyViolationError
    from queue.batch_manager import BatchManager


def test_queue_add_and_count():
    q = BallotQueue()
    assert q.count() == 0

    item = q.add({
        "election_id": "ELECTION_2026",
        "encrypted_ballot": "ENC_BALLOT_001",
        "nullifier": "NULLIFIER_001",
    })
    assert q.count() == 1
    assert item["nullifier"] == "NULLIFIER_001"
    assert "timestamp" in item


def test_queue_rejects_pii():
    q = BallotQueue()

    # Attempting to add voter_id
    with pytest.raises(PrivacyViolationError, match="Forbidden field 'voter_id' detected"):
        q.add({
            "election_id": "ELECTION_2026",
            "encrypted_ballot": "ENC_BALLOT_001",
            "nullifier": "NULLIFIER_001",
            "voter_id": "VOTER_12345",
        })

    # Attempting to add biometric/iris
    with pytest.raises(PrivacyViolationError, match="Forbidden field 'iris' detected"):
        q.add({
            "election_id": "ELECTION_2026",
            "encrypted_ballot": "ENC_BALLOT_001",
            "nullifier": "NULLIFIER_001",
            "iris": "IRIS_RAW_HASH_99",
        })

    # Attempting to add plaintext candidate
    with pytest.raises(PrivacyViolationError, match="Forbidden field 'candidate' detected"):
        q.add({
            "election_id": "ELECTION_2026",
            "encrypted_ballot": "ENC_BALLOT_001",
            "nullifier": "NULLIFIER_001",
            "candidate": "Candidate A",
        })


def test_queue_duplicate_nullifier_rejection():
    q = BallotQueue()
    q.add({
        "election_id": "ELECTION_2026",
        "encrypted_ballot": "ENC_BALLOT_001",
        "nullifier": "NULLIFIER_001",
    })

    with pytest.raises(ValueError, match="already in the local queue"):
        q.add({
            "election_id": "ELECTION_2026",
            "encrypted_ballot": "ENC_BALLOT_002",
            "nullifier": "NULLIFIER_001",
        })


def test_batch_manager_shuffling():
    bm = BatchManager()
    ballots = [
        {"election_id": "E_26", "encrypted_ballot": f"ENC_{i}", "nullifier": f"NULL_{i}"}
        for i in range(20)
    ]

    shuffled = bm.shuffle_ballots(ballots)
    assert len(shuffled) == len(ballots)
    # Check that elements are preserved
    assert set(b["nullifier"] for b in shuffled) == set(b["nullifier"] for b in ballots)


def test_batch_creation():
    bm = BatchManager()
    ballots = [
        {"election_id": "E_26", "encrypted_ballot": "ENC_1", "nullifier": "NULL_1"},
        {"election_id": "E_26", "encrypted_ballot": "ENC_2", "nullifier": "NULL_2"},
    ]

    batch = bm.create_batch(ballots, batch_id="BATCH_TEST_99")
    assert batch["batch_id"] == "BATCH_TEST_99"
    assert batch["count"] == 2
    assert "NULL_1" in batch["nullifiers"]
    assert "NULL_2" in batch["nullifiers"]
