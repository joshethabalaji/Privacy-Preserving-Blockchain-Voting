"""
Blockchain Service (Person 3)
Interacts with local Ganache blockchain using Web3.py.
Handles transaction signing, confirmation verification, and state querying.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from web3 import Web3
from web3.exceptions import ContractLogicError

from backend.config import settings

logger = logging.getLogger("blockchain_service")


class BlockchainService:
    def __init__(self):
        self.w3: Optional[Web3] = None
        self.contract = None
        self.abi = None
        self.contract_address = None
        self.account = None
        self.private_key = None
        self.rpc_url = settings.GANACHE_RPC_URL
        self._init_web3()

    def _init_web3(self):
        """Initializes connection to Ganache RPC and loads contract."""
        try:
            self.w3 = Web3(Web3.HTTPProvider(self.rpc_url))
            if not self.w3.is_connected():
                # Try fallback port 8545
                alt_url = "http://127.0.0.1:8545"
                w3_alt = Web3(Web3.HTTPProvider(alt_url))
                if w3_alt.is_connected():
                    self.w3 = w3_alt
                    self.rpc_url = alt_url
                    logger.info(f"Connected to alternate Ganache RPC: {alt_url}")
            
            if self.w3.is_connected():
                logger.info(f"Connected to Ganache at: {self.rpc_url}")
                self._load_account()
                self._load_contract()
        except Exception as e:
            logger.warning(f"Initial Web3 connection warning: {e}")

    def _load_account(self):
        """Loads development account and private key."""
        self.account = settings.BLOCKCHAIN_ACCOUNT
        self.private_key = settings.PRIVATE_KEY

        if not self.account or not self.account.startswith("0x") or len(self.account) != 42:
            if self.w3 and self.w3.is_connected() and len(self.w3.eth.accounts) > 0:
                self.account = self.w3.eth.accounts[0]
                logger.info(f"Using default Ganache account: {self.account}")

    def _load_contract(self):
        """Loads compiled ABI and instantiates contract if address is configured."""
        abi_path = settings.ABI_FILE
        if not abi_path.exists():
            logger.warning(f"ABI file not found at {abi_path}")
            return

        with open(abi_path, "r", encoding="utf-8") as f:
            contract_data = json.load(f)
            self.abi = contract_data.get("abi")

        # Try address from settings or latest_deployment.json
        self.contract_address = settings.CONTRACT_ADDRESS
        if not self.contract_address:
            deployment_file = settings.BASE_DIR / "blockchain" / "deployment" / "latest_deployment.json"
            if deployment_file.exists():
                try:
                    with open(deployment_file, "r", encoding="utf-8") as df:
                        dep_data = json.load(df)
                        self.contract_address = dep_data.get("contractAddress")
                except Exception:
                    pass

        if self.w3 and self.w3.is_connected() and self.abi and self.contract_address:
            try:
                checksum_address = self.w3.to_checksum_address(self.contract_address)
                self.contract = self.w3.eth.contract(address=checksum_address, abi=self.abi)
                logger.info(f"Contract loaded at address: {checksum_address}")
            except Exception as e:
                logger.error(f"Failed to load contract at {self.contract_address}: {e}")

    def is_connected(self) -> bool:
        """Returns True if connected to Ganache."""
        return bool(self.w3 and self.w3.is_connected())

    def get_network_info(self) -> Dict[str, Any]:
        """Returns node and blockchain network info."""
        if not self.is_connected():
            return {
                "connected": False,
                "rpc_url": self.rpc_url,
                "block_number": None,
                "contract_address": self.contract_address,
                "account": self.account,
            }
        return {
            "connected": True,
            "rpc_url": self.rpc_url,
            "block_number": self.w3.eth.block_number,
            "contract_address": self.contract_address,
            "account": self.account,
            "chain_id": self.w3.eth.chain_id,
        }

    def _send_transaction(self, contract_func, *args) -> Tuple[str, Any]:
        """
        Executes a state-mutating transaction, signs if private key available,
        and waits for on-chain receipt confirmation.
        """
        if not self.is_connected():
            raise ConnectionError("Not connected to Ganache blockchain.")
        if not self.contract:
            raise ValueError("Voting smart contract is not loaded or deployed.")

        # Ensure account is ready
        self._load_account()
        account = self.w3.to_checksum_address(self.account)

        try:
            if self.private_key and self.private_key.startswith("0x") and len(self.private_key) == 66:
                nonce = self.w3.eth.get_transaction_count(account)
                tx = contract_func(*args).build_transaction({
                    "from": account,
                    "nonce": nonce,
                    "gas": 3000000,
                    "gasPrice": self.w3.eth.gas_price or self.w3.to_wei("20", "gwei"),
                })
                signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=self.private_key)
                tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            else:
                tx_hash = contract_func(*args).transact({"from": account, "gas": 3000000})

            tx_hash_hex = tx_hash.hex()
            logger.info(f"Transaction submitted: {tx_hash_hex}. Awaiting confirmation...")
            
            # Wait for receipt
            receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=30)
            
            if receipt.status != 1:
                raise RuntimeError(
                    f"Blockchain transaction failed. Vote was not confirmed. (Status: {receipt.status})"
                )

            return tx_hash_hex, receipt

        except ContractLogicError as cle:
            error_msg = str(cle)
            logger.error(f"Smart contract revert: {error_msg}")
            raise ValueError(f"Contract error: {error_msg}")
        except Exception as e:
            logger.error(f"Transaction execution error: {e}")
            raise

    def start_election(self, election_id: str) -> Dict[str, Any]:
        """Starts an election on the smart contract."""
        tx_hash, receipt = self._send_transaction(self.contract.functions.startElection, election_id)
        return {
            "success": True,
            "election_id": election_id,
            "transaction_hash": tx_hash,
            "block_number": receipt.blockNumber,
        }

    def end_election(self) -> Dict[str, Any]:
        """Ends the active election on the smart contract."""
        tx_hash, receipt = self._send_transaction(self.contract.functions.endElection)
        return {
            "success": True,
            "transaction_hash": tx_hash,
            "block_number": receipt.blockNumber,
        }

    def is_nullifier_used(self, nullifier: str, election_id: Optional[str] = None) -> bool:
        """
        Queries smart contract to check if nullifier is already used.
        """
        if not self.is_connected() or not self.contract:
            return False

        try:
            if election_id:
                return self.contract.functions.isNullifierUsedForElection(election_id, nullifier).call()
            return self.contract.functions.isNullifierUsed(nullifier).call()
        except Exception as e:
            logger.error(f"Error checking nullifier '{nullifier}': {e}")
            return False

    def record_vote(self, nullifier: str, encrypted_ballot: str, batch_id: str) -> Dict[str, Any]:
        """
        Records a single encrypted ballot with nullifier verification.
        """
        tx_hash, receipt = self._send_transaction(
            self.contract.functions.recordVote, nullifier, encrypted_ballot, batch_id
        )
        return {
            "success": True,
            "transaction_hash": tx_hash,
            "block_number": receipt.blockNumber,
            "gas_used": receipt.gasUsed,
            "batch_id": batch_id,
            "nullifier": nullifier,
        }

    def record_batch(
        self, batch_id: str, nullifiers: List[str], encrypted_ballots: List[str]
    ) -> Dict[str, Any]:
        """
        Records a batch of encrypted ballots atomically.
        """
        tx_hash, receipt = self._send_transaction(
            self.contract.functions.recordBatch, batch_id, nullifiers, encrypted_ballots
        )
        return {
            "success": True,
            "batch_id": batch_id,
            "count": len(nullifiers),
            "transaction_hash": tx_hash,
            "block_number": receipt.blockNumber,
            "gas_used": receipt.gasUsed,
        }

    def get_election_status(self) -> Dict[str, Any]:
        """Queries on-chain election state."""
        if not self.is_connected() or not self.contract:
            return {"status": "NOT_CONNECTED", "election_id": None}

        try:
            status_str, election_id = self.contract.functions.getElectionStatus().call()
            return {"status": status_str, "election_id": election_id}
        except Exception as e:
            logger.error(f"Error fetching election status: {e}")
            return {"status": "ERROR", "error": str(e)}

    def get_vote_records(self) -> List[Dict[str, Any]]:
        """Queries on-chain recorded votes."""
        if not self.is_connected() or not self.contract:
            return []

        try:
            raw_records = self.contract.functions.getVoteRecords().call()
            records = []
            for r in raw_records:
                records.append({
                    "nullifier": r[0],
                    "encrypted_ballot": r[1],
                    "batch_id": r[2],
                    "timestamp": r[3],
                    "block_number": r[4],
                })
            return records
        except Exception as e:
            logger.error(f"Error fetching vote records: {e}")
            return []

    def get_vote_count(self) -> int:
        """Returns total on-chain vote count."""
        if not self.is_connected() or not self.contract:
            return 0
        try:
            return self.contract.functions.getVoteCount().call()
        except Exception:
            return 0


# Global singleton instance
blockchain_service = BlockchainService()
