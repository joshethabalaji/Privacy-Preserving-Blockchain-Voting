"""
Unit tests for Nullifier-Based Double-Vote Protection (Person 3).
Verifies that smart contract and backend actively reject reused nullifiers.
"""

import pytest
from web3.exceptions import ContractLogicError


def test_nullifier_replay_protection_on_contract(w3_ganache, deployed_contract):
    contract, _, admin = deployed_contract

    # Reset/Start new test election
    status, _ = contract.functions.getElectionStatus().call()
    if status != "ACTIVE":
        tx = contract.functions.startElection("ELECTION_NULLIFIER_TEST").transact({"from": admin})
        w3_ganache.eth.wait_for_transaction_receipt(tx)

    test_nullifier = "NULLIFIER_REPLAY_TEST_001"
    test_ballot = "ENC_BALLOT_TEST_001"

    # 1. Nullifier initially unused
    assert contract.functions.isNullifierUsed(test_nullifier).call() is False

    # 2. First submission should succeed
    tx1 = contract.functions.recordVote(test_nullifier, test_ballot, "BATCH_NULL_01").transact({"from": admin})
    receipt1 = w3_ganache.eth.wait_for_transaction_receipt(tx1)
    assert receipt1.status == 1
    assert contract.functions.isNullifierUsed(test_nullifier).call() is True

    # 3. Second submission with same nullifier MUST revert
    with pytest.raises(ContractLogicError, match="Vote rejected: nullifier has already been used."):
        contract.functions.recordVote(test_nullifier, "ENC_BALLOT_DIFFERENT", "BATCH_NULL_01").transact({"from": admin})

    # 4. A different nullifier should be accepted
    diff_nullifier = "NULLIFIER_REPLAY_TEST_002"
    tx2 = contract.functions.recordVote(diff_nullifier, test_ballot, "BATCH_NULL_01").transact({"from": admin})
    receipt2 = w3_ganache.eth.wait_for_transaction_receipt(tx2)
    assert receipt2.status == 1
    assert contract.functions.isNullifierUsed(diff_nullifier).call() is True
