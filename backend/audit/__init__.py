"""
Audit package initialization for Person 3 module.
"""
from audit.audit_log import AuditLogger, AuditEntry
from audit.verification import verify_audit_chain, run_tamper_demonstration

__all__ = ["AuditLogger", "AuditEntry", "verify_audit_chain", "run_tamper_demonstration"]
