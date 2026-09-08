"""
Audit Verification & Educational Tamper Detection Module (Person 3)
Provides cryptographic verification of the SHA-256 hash chain and educational simulation.
"""

import copy
import json
import hashlib
from typing import List, Dict, Any, Tuple
from audit.audit_log import GENESIS_PREV_HASH, AuditEntry


def recalculate_entry_hash(prev_hash: str, timestamp: float, event_type: str, event_data: Dict[str, Any]) -> str:
    """Computes expected SHA-256 hash for an entry."""
    canonical_data = json.dumps(event_data, sort_keys=True)
    raw_payload = f"{prev_hash}|{timestamp:.6f}|{event_type}|{canonical_data}"
    return hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()


def verify_audit_chain(chain_dicts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Verifies the cryptographic integrity of an entire audit log hash chain.
    """
    if not chain_dicts:
        return {
            "verified": False,
            "total_entries": 0,
            "broken_index": None,
            "message": "Audit chain is empty.",
        }

    # Verify Genesis entry
    genesis = chain_dicts[0]
    if genesis.get("prev_hash") != GENESIS_PREV_HASH:
        return {
            "verified": False,
            "total_entries": len(chain_dicts),
            "broken_index": 0,
            "message": f"Genesis block prev_hash invalid. Expected {GENESIS_PREV_HASH}",
        }

    # Verify each link in the chain
    for i in range(1, len(chain_dicts)):
        prev_entry = chain_dicts[i - 1]
        curr_entry = chain_dicts[i]

        # 1. Verify link continuity
        if curr_entry.get("prev_hash") != prev_entry.get("entry_hash"):
            return {
                "verified": False,
                "total_entries": len(chain_dicts),
                "broken_index": i,
                "message": (
                    f"Hash continuity broken at entry {i}! "
                    f"Previous hash in entry ({curr_entry.get('prev_hash')[:16]}...) "
                    f"does not match actual hash of entry {i-1} ({prev_entry.get('entry_hash')[:16]}...)"
                ),
            }

        # 2. Recalculate and verify self hash
        expected_hash = recalculate_entry_hash(
            curr_entry["prev_hash"],
            curr_entry["timestamp"],
            curr_entry["event_type"],
            curr_entry["event_data"],
        )

        if expected_hash != curr_entry.get("entry_hash"):
            return {
                "verified": False,
                "total_entries": len(chain_dicts),
                "broken_index": i,
                "message": (
                    f"Content tampering detected at entry {i}! "
                    f"Recalculated SHA-256 ({expected_hash[:16]}...) "
                    f"does not match stored hash ({curr_entry.get('entry_hash')[:16]}...)"
                ),
            }

    return {
        "verified": True,
        "total_entries": len(chain_dicts),
        "broken_index": None,
        "message": f"Audit log verified successfully ({len(chain_dicts)} entries). No tampering detected.",
    }


def run_tamper_demonstration(chain_dicts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Simulates a safe, educational tamper detection experiment in local memory.
    Demonstrates that modifying any historical record immediately invalidates the cryptographic chain.
    """
    if len(chain_dicts) < 2:
        return {
            "success": False,
            "message": "Need at least 2 audit entries (Genesis + 1 event) to run tamper demonstration.",
        }

    # Verify original chain
    original_verification = verify_audit_chain(chain_dicts)

    # Make a deep copy to simulate an attacker altering an offline audit log entry
    tampered_chain = copy.deepcopy(chain_dicts)
    target_index = 1 if len(tampered_chain) == 2 else len(tampered_chain) // 2

    original_entry_data = copy.deepcopy(tampered_chain[target_index]["event_data"])
    tampered_entry_data = copy.deepcopy(original_entry_data)
    tampered_entry_data["_TAMPER_SIMULATION"] = "ATTACKER_ALTERED_PAYLOAD_VAL_999"

    tampered_chain[target_index]["event_data"] = tampered_entry_data

    # Verify tampered chain
    tampered_verification = verify_audit_chain(tampered_chain)

    return {
        "success": True,
        "simulation_label": "Educational Tamper Detection Simulation",
        "target_index": target_index,
        "before_tampering": {
            "entry_index": target_index,
            "event_data": original_entry_data,
            "verification": original_verification,
        },
        "after_tampering": {
            "entry_index": target_index,
            "tampered_data": tampered_entry_data,
            "verification": tampered_verification,
        },
        "explanation": (
            "Because SHA-256 is collision-resistant and avalanche-sensitive, "
            "any unauthorized modification to an event's payload alters its recalculated hash, "
            "breaking both its own hash match and all downstream chain links."
        ),
    }
