"""
Tests for Blockchain Submission Failure and Confirmation Guarantee (Person 3).
Verifies that if blockchain submission fails, Person 1 is NEVER notified to mark has_voted=true.
"""

import pytest
from unittest.mock import patch
from backend.services.batch_service import BatchService
from backend.services.notification_service import NotificationService
from backend.services.queue_service import QueueService, queue_service

try:
    from ballot_queue import BallotQueue
except ImportError:
    from queue.ballot_queue import BallotQueue


def test_blockchain_failure_does_not_trigger_person1_confirmation():
    """
    Simulates a failure during on-chain submission and confirms that
    Person 1 notification count does not increase.
    """
    notif_svc = NotificationService()
    queue_service.clear()
    queue_service.add_ballot({
        "election_id": "ELECTION_FAIL_TEST",
        "encrypted_ballot": "ENC_FAIL_01",
        "nullifier": "NULL_FAIL_01",
    })

    initial_notifs_count = len(notif_svc.get_notification_history())

    from backend.services.blockchain_service import blockchain_service

    # Mock blockchain_service.record_batch to simulate an EVM revert / failure
    with patch.object(blockchain_service, "record_batch") as mock_record:
        mock_record.side_effect = RuntimeError("Ganache RPC transaction reverted: Out of gas")

        batch_svc = BatchService()
        with patch.object(batch_svc, "batch_manager") as mock_bm:
            mock_bm.create_batch.return_value = {
                "batch_id": "BATCH_FAIL_01",
                "election_id": "ELECTION_FAIL_TEST",
                "nullifiers": ["NULL_FAIL_01"],
                "encrypted_ballots": ["ENC_FAIL_01"],
                "count": 1,
            }

            with pytest.raises(RuntimeError, match="Blockchain transaction failed. Vote was not confirmed"):
                batch_svc.process_queue(batch_id="BATCH_FAIL_01")

    # Verify that Person 1 notification was NOT triggered
    final_notifs_count = len(notif_svc.get_notification_history())
    assert final_notifs_count == initial_notifs_count
