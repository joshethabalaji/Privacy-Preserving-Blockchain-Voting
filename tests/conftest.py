"""
Pytest configuration and shared fixtures for Person 3 testing.
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import os
import json
import pytest
from web3 import Web3
from fastapi.testclient import TestClient

from backend.config import settings
from backend.app import app
from backend.services.blockchain_service import BlockchainService
from backend.services.audit_service import AuditService
from backend.services.queue_service import QueueService
from backend.services.batch_service import BatchService
from backend.services.notification_service import NotificationService


@pytest.fixture(scope="session")
def w3_ganache():
    """Provides a Web3 instance connected to Ganache."""
    url = settings.GANACHE_RPC_URL
    w3 = Web3(Web3.HTTPProvider(url))
    if not w3.is_connected():
        alt_url = "http://127.0.0.1:8545"
        w3_alt = Web3(Web3.HTTPProvider(alt_url))
        if w3_alt.is_connected():
            return w3_alt
        pytest.skip(f"Ganache not running at {url} or {alt_url}. Run 'npx ganache' or start Ganache UI.")
    return w3


@pytest.fixture(scope="function")
def deployed_contract(w3_ganache):
    """Deploys a fresh instance of Voting.sol for each test."""
    abi_file = settings.ABI_FILE
    if not abi_file.exists():
        from blockchain.deployment.compile import compile_contract
        compile_contract()

    with open(abi_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    abi = data["abi"]
    bytecode = data["bytecode"]
    account = w3_ganache.eth.accounts[0]

    voting_contract = w3_ganache.eth.contract(abi=abi, bytecode=bytecode)
    tx_hash = voting_contract.constructor().transact({"from": account, "gas": 3000000})
    receipt = w3_ganache.eth.wait_for_transaction_receipt(tx_hash)
    contract_address = receipt.contractAddress
    contract_inst = w3_ganache.eth.contract(address=contract_address, abi=abi)

    # Sync with global blockchain_service instance used by FastAPI
    from backend.services.blockchain_service import blockchain_service
    blockchain_service.w3 = w3_ganache
    blockchain_service.contract = contract_inst
    blockchain_service.contract_address = contract_address
    blockchain_service.account = account

    return contract_inst, contract_address, account


@pytest.fixture
def client():
    """Provides FastAPI TestClient."""
    return TestClient(app)
