"""
Audit Routes (Person 3)
Provides endpoints to inspect the SHA-256 hash chain, run cryptographic verification,
and execute educational safe tamper-detection experiments.
"""

from fastapi import APIRouter, HTTPException, status
from backend.services.audit_service import audit_service

router = APIRouter(prefix="/api/audit", tags=["Audit"])


@router.get("")
def get_audit_log():
    """Returns the full SHA-256 hash-chained voting audit trail."""
    chain = audit_service.get_chain()
    return {
        "count": len(chain),
        "chain": chain,
    }


@router.get("/verify")
def verify_audit_log():
    """
    Cryptographically recalculates and verifies each SHA-256 link in the audit chain.
    """
    result = audit_service.verify_chain()
    return result


@router.post("/tamper-demo")
def tamper_detection_simulation():
    """
    Runs a safe educational simulation demonstrating tamper detection.
    Clones the chain in memory, modifies a historical payload, and verifies the break.
    """
    result = audit_service.run_tamper_demo()
    return result


@router.post("/reset")
def reset_audit_log():
    """Resets audit chain to genesis (development only)."""
    audit_service.reset()
    return {"success": True, "message": "Audit chain reset to genesis block."}
