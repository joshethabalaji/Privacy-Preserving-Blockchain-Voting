"""
Unit tests for Hash-Chained Audit Log & Verification (Person 3).
"""

from audit.audit_log import AuditLogger, GENESIS_PREV_HASH
from audit.verification import verify_audit_chain, run_tamper_demonstration


def test_genesis_block():
    logger = AuditLogger()
    chain = logger.get_chain()
    assert len(chain) == 1
    assert chain[0]["index"] == 0
    assert chain[0]["prev_hash"] == GENESIS_PREV_HASH
    assert chain[0]["event_type"] == "GENESIS_BLOCK"


def test_chaining_events():
    logger = AuditLogger()
    e1 = logger.log_event("BALLOT_QUEUED", {"nullifier": "NULL_01", "election_id": "E_26"})
    e2 = logger.log_event("BATCH_SUBMITTED", {"batch_id": "B_01", "count": 1})

    chain = logger.get_chain()
    assert len(chain) == 3
    assert chain[1]["prev_hash"] == chain[0]["entry_hash"]
    assert chain[2]["prev_hash"] == chain[1]["entry_hash"]


def test_audit_verification_success():
    logger = AuditLogger()
    logger.log_event("BALLOT_QUEUED", {"nullifier": "NULL_01"})
    logger.log_event("BATCH_CREATED", {"batch_id": "BATCH_01"})
    logger.log_event("BLOCKCHAIN_CONFIRMED", {"tx_hash": "0xabc", "block_number": 10})

    chain = logger.get_chain()
    res = verify_audit_chain(chain)
    assert res["verified"] is True
    assert res["broken_index"] is None
    assert "verified successfully" in res["message"]


def test_tamper_detection_simulation():
    logger = AuditLogger()
    logger.log_event("BALLOT_QUEUED", {"nullifier": "NULL_01"})
    logger.log_event("BATCH_SUBMITTED", {"batch_id": "BATCH_01"})

    chain = logger.get_chain()
    sim_res = run_tamper_demonstration(chain)

    assert sim_res["success"] is True
    assert sim_res["before_tampering"]["verification"]["verified"] is True
    assert sim_res["after_tampering"]["verification"]["verified"] is False
    assert sim_res["after_tampering"]["verification"]["broken_index"] is not None
