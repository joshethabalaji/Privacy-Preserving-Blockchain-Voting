"""
Blockchain Inspection & Simulated Tally Routes (Person 3)
Allows querying immutable blockchain records and simulated tally visualization.
"""

from collections import Counter
from fastapi import APIRouter, HTTPException
from backend.services.blockchain_service import blockchain_service

router = APIRouter(prefix="/api", tags=["Blockchain & Tally"])


@router.get("/blockchain/audit")
def get_blockchain_audit():
    """
    Returns on-chain recorded votes and batch metadata.
    Zero voter PII or candidate plaintext is exposed.
    """
    votes = blockchain_service.get_vote_records()
    network_info = blockchain_service.get_network_info()
    return {
        "connected": network_info.get("connected"),
        "total_votes_on_chain": len(votes),
        "contract_address": network_info.get("contract_address"),
        "current_block": network_info.get("block_number"),
        "records": votes,
    }


@router.get("/blockchain/verify")
def verify_blockchain_state():
    """Verifies that on-chain record count matches queryable state."""
    count = blockchain_service.get_vote_count()
    records = blockchain_service.get_vote_records()
    return {
        "verified": len(records) == count,
        "on_chain_count": count,
        "fetched_records_count": len(records),
        "message": "Blockchain state is consistent." if len(records) == count else "State mismatch detected.",
    }


@router.get("/results")
def get_simulated_tally():
    """
    Returns SIMULATED tally visualization for prototype demonstration.
    
    IMPORTANT NOTE:
    Person 2 owns the private decryption key for encrypted ballots.
    Person 3 does NOT possess decryption keys and cannot decrypt real ballots on-chain.
    This endpoint aggregates ciphertext frequencies and maps them to simulated demo labels.
    """
    records = blockchain_service.get_vote_records()
    if not records:
        return {
            "disclaimer": "SIMULATED TALLY PROTOTYPE: Person 2 owns final cryptographic decryption.",
            "total_votes": 0,
            "tally": {},
            "ciphertext_counts": {},
        }

    # Count ciphertext distribution
    ciphertexts = [r["encrypted_ballot"] for r in records]
    counts = dict(Counter(ciphertexts))

    # Simulated candidate mapping for demonstration purposes only
    simulated_map = {
        "ENC_BALLOT_001": "Candidate Alpha (Simulated)",
        "ENC_BALLOT_002": "Candidate Beta (Simulated)",
        "ENC_BALLOT_003": "Candidate Gamma (Simulated)",
        "ENC_BALLOT_004": "Candidate Delta (Simulated)",
    }

    simulated_tally = {}
    for ctext, cnt in counts.items():
        label = simulated_map.get(ctext, f"Encrypted Ciphertext ({ctext[:8]}...)")
        simulated_tally[label] = cnt

    return {
        "disclaimer": "SIMULATED TALLY PROTOTYPE: Person 2 owns final cryptographic decryption.",
        "total_votes": len(records),
        "tally": simulated_tally,
        "ciphertext_counts": counts,
    }
