"""
Audit Service (Person 3)
Wraps the SHA-256 hash-chained audit logger and provides verification/tamper detection endpoints.
"""

from typing import Dict, Any, List
from audit.audit_log import AuditLogger
from audit.verification import verify_audit_chain, run_tamper_demonstration

audit_logger = AuditLogger()


class AuditService:
    def __init__(self, logger: AuditLogger = audit_logger):
        self.logger = logger

    def log(self, event_type: str, event_data: Dict[str, Any]):
        return self.logger.log_event(event_type, event_data)

    def get_chain(self) -> List[Dict[str, Any]]:
        return self.logger.get_chain()

    def verify_chain(self) -> Dict[str, Any]:
        chain_data = self.get_chain()
        return verify_audit_chain(chain_data)

    def run_tamper_demo(self) -> Dict[str, Any]:
        chain_data = self.get_chain()
        return run_tamper_demonstration(chain_data)

    def reset(self):
        self.logger.reset_to_genesis()


audit_service = AuditService()
