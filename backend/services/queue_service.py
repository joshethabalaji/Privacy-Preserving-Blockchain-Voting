"""
Queue Service (Person 3)
Manages the temporary ballot queue and logs queueing events to the audit chain.
"""

from typing import Dict, Any, List
try:
    from ballot_queue import BallotQueue
except ImportError:
    from queue.ballot_queue import BallotQueue

from backend.services.audit_service import audit_service

ballot_queue = BallotQueue()


class QueueService:
    def __init__(self, q: BallotQueue = ballot_queue):
        self.queue = q

    def add_ballot(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Validates, adds ballot to queue, and logs the event."""
        item = self.queue.add(payload)
        
        # Log to audit trail (only nullifier and election_id)
        audit_service.log(
            event_type="BALLOT_QUEUED",
            event_data={
                "election_id": item["election_id"],
                "nullifier": item["nullifier"],
                "queue_count": self.queue.count(),
            },
        )
        return item

    def get_queue(self) -> List[Dict[str, Any]]:
        return self.queue.get_all()

    def get_count(self) -> int:
        return self.queue.count()

    def remove_ballots(self, nullifiers: List[str]) -> int:
        return self.queue.remove_items(nullifiers)

    def clear(self):
        self.queue.clear()


queue_service = QueueService()
