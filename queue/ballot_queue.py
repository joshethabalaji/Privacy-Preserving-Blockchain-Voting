"""
Protected Ballot Queue Module (Person 3)
Stores incoming encrypted ballots in temporary memory prior to shuffling and batching.
Enforces strict privacy boundaries by rejecting any personally identifiable information (PII).
"""

import time
import threading
from typing import List, Dict, Any, Optional

FORBIDDEN_PII_FIELDS = {
    "voter_id",
    "voterid",
    "name",
    "voter_name",
    "address",
    "age",
    "iris",
    "iris_template",
    "iris_image",
    "biometric",
    "phone",
    "email",
    "password",
    "temporary_authorization",
    "auth_token",
    "candidate",
    "candidate_name",
    "candidate_id",
}


class PrivacyViolationError(ValueError):
    """Raised when an attempt is made to insert PII into the voting queue."""
    pass


class BallotQueue:
    """
    Thread-safe in-memory queue holding protected ballot payloads.
    Only holds: election_id, encrypted_ballot, nullifier, and timestamp.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._queue: List[Dict[str, Any]] = []

    def validate_payload(self, data: Dict[str, Any]) -> None:
        """
        Validates that the payload contains required voting fields and zero PII.
        """
        if not isinstance(data, dict):
            raise ValueError("Queue item must be a JSON object / dictionary")

        # Check for forbidden PII keys (case-insensitive)
        for key in data.keys():
            if key.lower() in FORBIDDEN_PII_FIELDS:
                raise PrivacyViolationError(
                    f"Privacy Violation: Forbidden field '{key}' detected. Person 3 must not receive PII."
                )

        required_fields = ["election_id", "encrypted_ballot", "nullifier"]
        for field in required_fields:
            val = data.get(field)
            if not val or not isinstance(val, str) or not val.strip():
                raise ValueError(f"Missing or empty required field: '{field}'")

    def add(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adds a validated protected ballot to the temporary queue.
        """
        self.validate_payload(data)

        item = {
            "election_id": data["election_id"].strip(),
            "encrypted_ballot": data["encrypted_ballot"].strip(),
            "nullifier": data["nullifier"].strip(),
            "timestamp": time.time(),
        }

        with self._lock:
            # Check if this exact nullifier is already in the queue to prevent local duplicates
            for existing in self._queue:
                if (
                    existing["election_id"] == item["election_id"]
                    and existing["nullifier"] == item["nullifier"]
                ):
                    raise ValueError(
                        f"Duplicate nullifier '{item['nullifier']}' is already in the local queue."
                    )

            self._queue.append(item)
            return item

    def get_all(self) -> List[Dict[str, Any]]:
        """Returns a snapshot copy of all items in the queue."""
        with self._lock:
            return [dict(item) for item in self._queue]

    def count(self) -> int:
        """Returns current queue depth."""
        with self._lock:
            return len(self._queue)

    def remove_items(self, nullifiers: List[str]) -> int:
        """
        Removes items by nullifiers once submitted to blockchain.
        """
        with self._lock:
            initial_len = len(self._queue)
            nullifier_set = set(nullifiers)
            self._queue = [item for item in self._queue if item["nullifier"] not in nullifier_set]
            return initial_len - len(self._queue)

    def clear(self) -> None:
        """Clears the queue."""
        with self._lock:
            self._queue.clear()
