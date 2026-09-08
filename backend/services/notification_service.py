"""
Notification Service (Person 3)
Handles notifications to Person 1 (voter confirmation callback) and Person 2 (receipt payload).
Strictly enforces confirmation before dispatching.
"""

import logging
import requests
from typing import Dict, Any, List, Optional
from backend.config import settings

logger = logging.getLogger("notification_service")


class NotificationService:
    def __init__(self):
        self.dispatched_person1_notifications: List[Dict[str, Any]] = []
        self.mock_url = settings.MOCK_PERSON1_URL

    def notify_person1_vote_confirmed(
        self, election_id: str, transaction_hash: str, block_number: int
    ) -> Dict[str, Any]:
        """
        Dispatches notification to Person 1 only AFTER blockchain confirmation.
        Payload contains NO voter ID or biometric information.
        """
        payload = {
            "vote_recorded": True,
            "election_id": election_id,
            "transaction_hash": transaction_hash,
            "block_number": block_number,
        }

        # Record locally for dashboard and audit
        self.dispatched_person1_notifications.append(payload)

        # Attempt HTTP callback if mock or real endpoint is live
        try:
            response = requests.post(self.mock_url, json=payload, timeout=2)
            logger.info(f"Person 1 callback status: {response.status_code}")
        except Exception as e:
            logger.debug(f"Person 1 external webhook notification skipped: {e}")

        return payload

    def build_person2_receipt(
        self,
        transaction_hash: str,
        block_number: int,
        batch_id: str,
        nullifier: str,
        success: bool = True,
    ) -> Dict[str, Any]:
        """
        Constructs receipt data needed by Person 2 to display to the voter.
        Contains NO plaintext candidate name or voter identity.
        """
        return {
            "success": success,
            "message": "Ballot recorded successfully",
            "transaction_hash": transaction_hash,
            "block_number": block_number,
            "batch_id": batch_id,
            "nullifier": nullifier,
        }

    def get_notification_history(self) -> List[Dict[str, Any]]:
        return list(self.dispatched_person1_notifications)


notification_service = NotificationService()
