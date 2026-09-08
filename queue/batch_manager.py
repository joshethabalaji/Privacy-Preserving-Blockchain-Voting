"""
Batch Manager Module (Person 3)
Handles secure shuffling and batch packaging for queued encrypted ballots.
"""

import secrets
import time
from typing import List, Dict, Any, Tuple


class BatchManager:
    """
    Manages cryptographically secure shuffling of ballots and batch creation.
    """

    def __init__(self):
        self._batch_counter = 0
        self._crypto_random = secrets.SystemRandom()

    def generate_batch_id(self, prefix: str = "BATCH") -> str:
        """Generates a sequential and unique batch identifier."""
        self._batch_counter += 1
        return f"{prefix}_{self._batch_counter:03d}"

    def shuffle_ballots(self, ballots: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Randomly shuffles ballots using OS cryptographic randomness (secrets.SystemRandom).
        Decouples arrival time order from blockchain recording order.
        Does not mutate the original input list or the internal ballot contents.
        """
        if not ballots:
            return []
        shuffled = [dict(b) for b in ballots]
        self._crypto_random.shuffle(shuffled)
        return shuffled

    def create_batch(
        self,
        ballots: List[Dict[str, Any]],
        batch_id: str = None,
        max_batch_size: int = 10,
    ) -> Dict[str, Any]:
        """
        Shuffles ballots and packages them into a batch dictionary.
        """
        if not ballots:
            raise ValueError("Cannot create an empty batch.")

        selected = ballots[:max_batch_size]
        shuffled = self.shuffle_ballots(selected)
        bid = batch_id or self.generate_batch_id()

        batch_payload = {
            "batch_id": bid,
            "election_id": shuffled[0]["election_id"],
            "count": len(shuffled),
            "ballots": shuffled,
            "nullifiers": [b["nullifier"] for b in shuffled],
            "encrypted_ballots": [b["encrypted_ballot"] for b in shuffled],
            "created_at": time.time(),
        }
        return batch_payload
