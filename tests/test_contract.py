"""
Unit tests for Voting.sol Solidity Smart Contract.
Tests compilation, deployment, state transitions, access control, and batch recording.
"""

import pytest
from web3.exceptions import ContractLogicError


def test_contract_initial_state(deployed_contract):
    contract, address, admin = deployed_contract
    assert contract.functions.admin().call() == admin
    status, election_id = contract.functions.getElectionStatus().call()
    assert status == "NOT_STARTED"
    assert election_id == ""


def test_start_election(deployed_contract, w3_ganache):
    contract, _, admin = deployed_contract
    tx_hash = contract.functions.startElection("ELECTION_TEST_2026").transact({"from": admin})
    w3_ganache.eth.wait_for_transaction_receipt(tx_hash)

    status, election_id = contract.functions.getElectionStatus().call()
    assert status == "ACTIVE"
    assert election_id == "ELECTION_TEST_2026"


def test_record_vote_success(deployed_contract, w3_ganache):
    contract, _, admin = deployed_contract
    # Ensure active
    st, _ = contract.functions.getElectionStatus().call()
    if st != "ACTIVE":
        tx = contract.functions.startElection("ELECTION_TEST_2026").transact({"from": admin})
        w3_ganache.eth.wait_for_transaction_receipt(tx)

    tx_hash = contract.functions.recordVote("NULL_SOL_01", "ENC_SOL_01", "BATCH_01").transact({"from": admin})
    receipt = w3_ganache.eth.wait_for_transaction_receipt(tx_hash)
    assert receipt.status == 1

    assert contract.functions.isNullifierUsed("NULL_SOL_01").call() is True
    assert contract.functions.getVoteCount().call() == 1


def test_record_batch_success(deployed_contract, w3_ganache):
    contract, _, admin = deployed_contract
    # Ensure active
    st, _ = contract.functions.getElectionStatus().call()
    if st != "ACTIVE":
        tx = contract.functions.startElection("ELECTION_TEST_2026").transact({"from": admin})
        w3_ganache.eth.wait_for_transaction_receipt(tx)

    nullifiers = ["NULL_BATCH_01", "NULL_BATCH_02"]
    ballots = ["ENC_BATCH_01", "ENC_BATCH_02"]
    tx_hash = contract.functions.recordBatch("BATCH_TEST_02", nullifiers, ballots).transact({"from": admin})
    receipt = w3_ganache.eth.wait_for_transaction_receipt(tx_hash)
    assert receipt.status == 1

    batch_info = contract.functions.getBatchInformation("BATCH_TEST_02").call()
    assert batch_info[0] == "BATCH_TEST_02"
    assert batch_info[1] == 2


def test_end_election(deployed_contract, w3_ganache):
    contract, _, admin = deployed_contract
    # Ensure active first
    st, _ = contract.functions.getElectionStatus().call()
    if st != "ACTIVE":
        tx = contract.functions.startElection("ELECTION_TEST_2026").transact({"from": admin})
        w3_ganache.eth.wait_for_transaction_receipt(tx)

    tx_hash = contract.functions.endElection().transact({"from": admin})
    receipt = w3_ganache.eth.wait_for_transaction_receipt(tx_hash)
    assert receipt.status == 1

    status, _ = contract.functions.getElectionStatus().call()
    assert status == "ENDED"


def test_vote_after_election_ended_reverts(deployed_contract, w3_ganache):
    contract, _, admin = deployed_contract
    # Ensure ended or not started
    st, _ = contract.functions.getElectionStatus().call()
    if st == "ACTIVE":
        tx = contract.functions.endElection().transact({"from": admin})
        w3_ganache.eth.wait_for_transaction_receipt(tx)

    with pytest.raises(ContractLogicError, match="Election is not active"):
        contract.functions.recordVote("NULL_FAIL", "ENC_FAIL", "BATCH_FAIL").transact({"from": admin})
