"""
Pydantic Schemas for Person 3 APIs.
Enforces strict schema validation and actively forbids any PII attributes.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class VoteSubmissionRequest(StrictBaseModel):
    election_id: str = Field(..., description="Target election identifier, e.g., 'ELECTION_2026'")
    encrypted_ballot: str = Field(..., description="Encrypted ballot ciphertext, e.g., 'ENC_BALLOT_001'")
    nullifier: str = Field(..., description="Unique cryptographic nullifier, e.g., 'NULLIFIER_001'")
    batch_id: Optional[str] = Field("BATCH_DIRECT", description="Optional batch identifier")


class QueueAddRequest(StrictBaseModel):
    election_id: str = Field(..., description="Target election identifier")
    encrypted_ballot: str = Field(..., description="Simulated encrypted ballot string")
    nullifier: str = Field(..., description="Unique cryptographic nullifier")


class ProcessQueueRequest(StrictBaseModel):
    batch_id: Optional[str] = Field(None, description="Optional custom batch ID")
    max_batch_size: Optional[int] = Field(10, description="Maximum ballots to package into this batch")


class ElectionStartRequest(StrictBaseModel):
    election_id: str = Field(..., description="Unique election identifier to start, e.g. 'ELECTION_2026'")


class Person1ConfirmationPayload(StrictBaseModel):
    vote_recorded: bool
    election_id: str
    transaction_hash: str
    block_number: int


class Person2ReceiptResponse(StrictBaseModel):
    success: bool
    message: str
    transaction_hash: str
    block_number: int
    batch_id: str
    nullifier: str
