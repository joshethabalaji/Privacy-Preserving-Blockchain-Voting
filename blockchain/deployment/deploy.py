"""
Deployment script for Voting.sol on local Ganache blockchain.
"""

import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv, set_key
from web3 import Web3

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_PATH = BASE_DIR / ".env"
ABI_FILE = BASE_DIR / "blockchain" / "abi" / "Voting.json"

# Load environment variables
load_dotenv(dotenv_path=ENV_PATH)


def get_web3_connection(rpc_url=None):
    url = rpc_url or os.getenv("GANACHE_RPC_URL", "http://127.0.0.1:7545")
    w3 = Web3(Web3.HTTPProvider(url))
    if not w3.is_connected():
        # Try alternate default Ganache CLI port 8545
        alt_url = "http://127.0.0.1:8545"
        w3_alt = Web3(Web3.HTTPProvider(alt_url))
        if w3_alt.is_connected():
            return w3_alt, alt_url
        raise ConnectionError(
            f"Failed to connect to Ganache at {url} or {alt_url}. "
            "Please ensure Ganache is running (Ganache GUI on port 7545 or 'npx ganache' on port 8545)."
        )
    return w3, url


def deploy_contract(rpc_url=None):
    w3, active_rpc = get_web3_connection(rpc_url)
    print(f"[*] Connected to Ganache at: {active_rpc}")
    print(f"[*] Current Block Number: {w3.eth.block_number}")

    if not ABI_FILE.exists():
        print("[*] ABI not found, compiling contract first...")
        from blockchain.deployment.compile import compile_contract
        compile_contract()

    with open(ABI_FILE, "r", encoding="utf-8") as f:
        contract_data = json.load(f)

    abi = contract_data["abi"]
    bytecode = contract_data["bytecode"]

    account = os.getenv("BLOCKCHAIN_ACCOUNT")
    private_key = os.getenv("PRIVATE_KEY")

    # If no valid account provided or accounts exist on local testnode, auto-discover
    if not account or not account.startswith("0x") or len(account) != 42:
        if len(w3.eth.accounts) > 0:
            account = w3.eth.accounts[0]
            print(f"[*] Using unlocked Ganache test account: {account}")

    voting_contract = w3.eth.contract(abi=abi, bytecode=bytecode)

    print(f"[*] Deploying Voting contract from account: {account}...")
    
    if private_key and private_key.startswith("0x") and len(private_key) == 66:
        # Deploy using signed transaction
        nonce = w3.eth.get_transaction_count(account)
        tx = voting_contract.constructor().build_transaction({
            "from": account,
            "nonce": nonce,
            "gas": 3000000,
            "gasPrice": w3.eth.gas_price or w3.to_wei("20", "gwei"),
        })
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    else:
        # Deploy using unlocked test account (standard Ganache local test node)
        tx_hash = voting_contract.constructor().transact({"from": account, "gas": 3000000})

    print(f"[*] Transaction sent! Tx Hash: {tx_hash.hex()}")
    print("[*] Waiting for transaction confirmation...")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    if receipt.status != 1:
        raise RuntimeError(f"Contract deployment failed on blockchain! Status: {receipt.status}")

    contract_address = receipt.contractAddress
    print("=" * 60)
    print(f"[+] Voting Smart Contract Deployed Successfully!")
    print(f"[+] Contract Address: {contract_address}")
    print(f"[+] Block Number:     {receipt.blockNumber}")
    print(f"[+] Gas Used:         {receipt.gasUsed}")
    print(f"[+] Admin Account:    {account}")
    print("=" * 60)

    # Save to .env and deployment record
    deployment_record = {
        "contractAddress": contract_address,
        "transactionHash": tx_hash.hex(),
        "blockNumber": receipt.blockNumber,
        "adminAccount": account,
        "rpcUrl": active_rpc,
    }
    
    record_file = BASE_DIR / "blockchain" / "deployment" / "latest_deployment.json"
    with open(record_file, "w", encoding="utf-8") as f:
        json.dump(deployment_record, f, indent=2)

    # Update .env if it exists, otherwise create it
    if not ENV_PATH.exists():
        example_path = BASE_DIR / ".env.example"
        if example_path.exists():
            with open(example_path, "r", encoding="utf-8") as ef:
                with open(ENV_PATH, "w", encoding="utf-8") as nf:
                    nf.write(ef.read())
        else:
            with open(ENV_PATH, "w", encoding="utf-8") as nf:
                nf.write(f"GANACHE_RPC_URL={active_rpc}\n")

    set_key(str(ENV_PATH), "CONTRACT_ADDRESS", contract_address)
    set_key(str(ENV_PATH), "GANACHE_RPC_URL", active_rpc)
    set_key(str(ENV_PATH), "BLOCKCHAIN_ACCOUNT", account)

    print(f"[+] Updated configuration in: {ENV_PATH}")
    return contract_address, tx_hash.hex()


if __name__ == "__main__":
    try:
        deploy_contract()
    except Exception as e:
        print(f"[-] Deployment failed: {e}", file=sys.stderr)
        sys.exit(1)
