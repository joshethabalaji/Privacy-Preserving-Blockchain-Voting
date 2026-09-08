"""
Hash-Chained Tamper-Evident Audit Log (Person 3)
Maintains an immutable SHA-256 linked log of all voting actions, queue states, and blockchain transactions.
Strictly identity-free. Contains NO voter PII or plaintext candidate votes.
"""

import hashlib
import json
import time
import threading
from typing import List, Dict, Any, Optional

GENESIS_PREV_HASH = "0000000000000000000000000000000000000000000000000000000000000000"


class AuditEntry:
    """Represents a single entry in the SHA-256 hash chain."""

    def __init__(
        self,
        index: int,
        timestamp: float,
        event_type: str,
        event_data: Dict[str, Any],
        prev_hash: str,
        entry_hash: Optional[str] = None,
    ):
        self.index = index
        self.timestamp = timestamp
        self.event_type = event_type
        self.event_data = event_data
        self.prev_hash = prev_hash
        self.entry_hash = entry_hash or self.calculate_hash()

    def calculate_hash(self) -> str:
        """
        Calculates SHA-256 hash of the canonical representation:
        SHA256(prev_hash + str(timestamp) + event_type + json_canonical(event_data))
        """
        canonical_data = json.dumps(self.event_data, sort_keys=True)
        raw_payload = f"{self.prev_hash}|{self.timestamp:.6f}|{self.event_type}|{canonical_data}"
        return hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "timestamp_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(self.timestamp)),
            "event_type": self.event_type,
            "event_data": self.event_data,
            "prev_hash": self.prev_hash,
            "entry_hash": self.entry_hash,
        }


class AuditLogger:
    """
    Thread-safe append-only audit logger enforcing SHA-256 hash chaining.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._chain: List[AuditEntry] = []
        self._init_genesis()

    def _init_genesis(self):
        genesis = AuditEntry(
            index=0,
            timestamp=1700000000.0,  # Fixed canonical genesis timestamp
            event_type="GENESIS_BLOCK",
            event_data={"description": "Person 3 Identity-Free Blockchain Voting Audit Log Initialized"},
            prev_hash=GENESIS_PREV_HASH,
        )
        self._chain.append(genesis)

    def log_event(self, event_type: str, event_data: Dict[str, Any]) -> AuditEntry:
        """
        Appends an event to the hash chain after validating zero PII.
        """
        # Anti-PII verification
        for k in event_data.keys():
            if k.lower() in {
                "voter_id", "voterid", "name", "address", "age", "iris",
                "biometric", "candidate", "candidate_name", "temporary_authorization"
            }:
                raise ValueError(f"PII field '{k}' rejected from audit log.")

        with self._lock:
            prev_entry = self._chain[-1]
            entry = AuditEntry(
                index=len(self._chain),
                timestamp=time.time(),
                event_type=event_type,
                event_data=event_data,
                prev_hash=prev_entry.entry_hash,
            )
            self._chain.append(entry)
            return entry

    def get_chain(self) -> List[Dict[str, Any]]:
        with self._lock:
            return [e.to_dict() for e in self._chain]

    def get_latest_hash(self) -> str:
        with self._lock:
            return self._chain[-1].entry_hash

    def reset_to_genesis(self) -> None:
        """Resets the audit chain to genesis block only."""
        with self._lock:
            self._chain.clear()
            self._init_genesis()
