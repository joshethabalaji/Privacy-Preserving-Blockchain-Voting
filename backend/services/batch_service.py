"""
Batch Service (Person 3)
Coordinates queue extraction, secure shuffling, batch creation, blockchain submission,
audit chain logging, and external notifications upon on-chain confirmation.
"""

import logging
from typing import Dict, Any, List, Optional
try:
    from batch_manager import BatchManager
except ImportError:
    from queue.batch_manager import BatchManager

from backend.services.queue_service import queue_service
from backend.services.blockchain_service import blockchain_service
from backend.services.audit_service import audit_service
from backend.services.notification_service import notification_service

logger = logging.getLogger("batch_service")


class BatchService:
    def __init__(self):
        self.batch_manager = BatchManager()
        self.submitted_batches: List[Dict[str, Any]] = []

    def shuffle_current_queue(self) -> List[Dict[str, Any]]:
        """Shuffles all ballots in queue and returns the shuffled view."""
        current = queue_service.get_queue()
        if not current:
            return []
        shuffled = self.batch_manager.shuffle_ballots(current)
        # Update queue in memory
        queue_service.clear()
        for b in shuffled:
            queue_service.queue.add(b)
        
        audit_service.log(
            event_type="QUEUE_SHUFFLED",
            event_data={"count": len(shuffled), "action": "Randomized order decoupling arrival time"},
        )
        return shuffled

    def process_queue(
        self, batch_id: Optional[str] = None, max_batch_size: int = 10
    ) -> Dict[str, Any]:
        """
        Reads queued ballots, shuffles them, packages a batch, submits to Ganache,
        waits for confirmation, and dispatches Person 1 & Person 2 events.
        """
        queued_ballots = queue_service.get_queue()
        if not queued_ballots:
            raise ValueError("Cannot process an empty queue. Please add ballots first.")

        # 1. Shuffle and package batch
        batch = self.batch_manager.create_batch(
            queued_ballots, batch_id=batch_id, max_batch_size=max_batch_size
        )
        bid = batch["batch_id"]
        election_id = batch["election_id"]
        nullifiers = batch["nullifiers"]
        encrypted_ballots = batch["encrypted_ballots"]

        # 2. Check nullifiers against blockchain state first
        for n in nullifiers:
            if blockchain_service.is_nullifier_used(n, election_id):
                audit_service.log(
                    event_type="NULLIFIER_REJECTED",
                    event_data={"election_id": election_id, "nullifier": n, "reason": "Already used on blockchain"},
                )
                raise ValueError(f"Vote rejected: nullifier '{n}' has already been used.")

        audit_service.log(
            event_type="BATCH_CREATED",
            event_data={"batch_id": bid, "count": len(nullifiers), "election_id": election_id},
        )

        # 3. Submit to Blockchain and wait for confirmed receipt
        try:
            tx_result = blockchain_service.record_batch(bid, nullifiers, encrypted_ballots)
            tx_hash = tx_result["transaction_hash"]
            block_number = tx_result["block_number"]

            # 4. Log successful on-chain confirmation
            audit_service.log(
                event_type="BLOCKCHAIN_CONFIRMED",
                event_data={
                    "batch_id": bid,
                    "election_id": election_id,
                    "transaction_hash": tx_hash,
                    "block_number": block_number,
                    "count": len(nullifiers),
                },
            )

            # 5. Notify Person 1 (only because transaction status == 1 confirmed)
            p1_notification = notification_service.notify_person1_vote_confirmed(
                election_id=election_id,
                transaction_hash=tx_hash,
                block_number=block_number,
            )

            # 6. Build Person 2 receipts for each ballot in batch
            receipts = [
                notification_service.build_person2_receipt(
                    transaction_hash=tx_hash,
                    block_number=block_number,
                    batch_id=bid,
                    nullifier=n,
                )
                for n in nullifiers
            ]

            # 7. Remove submitted items from temporary queue
            queue_service.remove_ballots(nullifiers)

            summary = {
                "success": True,
                "message": f"Batch {bid} confirmed on blockchain!",
                "batch_id": bid,
                "election_id": election_id,
                "count": len(nullifiers),
                "transaction_hash": tx_hash,
                "block_number": block_number,
                "receipts": receipts,
                "person1_notified": True,
            }
            self.submitted_batches.append(summary)
            return summary

        except Exception as e:
            logger.error(f"Blockchain submission failed: {e}")
            audit_service.log(
                event_type="BLOCKCHAIN_SUBMISSION_FAILED",
                event_data={"batch_id": bid, "error": str(e)},
            )
            raise RuntimeError(
                f"Blockchain transaction failed. Vote was not confirmed. Error: {e}"
            )

    def get_submitted_batches(self) -> List[Dict[str, Any]]:
        return list(self.submitted_batches)


batch_service = BatchService()
