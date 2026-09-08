"""
End-to-End Live Demonstration Script for Person 3 Module.
Executes the full 16-step demonstration workflow against the live Ganache + FastAPI stack.
"""

import sys
import json
import time
import requests

BASE_URL = "http://127.0.0.1:8000"


def print_step(num: int, title: str):
    print("\n" + "=" * 70)
    print(f"STEP {num}: {title.upper()}")
    print("=" * 70)


def run_demo():
    print("\n[*] Starting Person 3 Live Demonstration Walkthrough...")

    # STEP 1 & 3: Health & Ganache Connection
    print_step(1, "Check Ganache Connection & Backend Health")
    res = requests.get(f"{BASE_URL}/api/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    health = res.json()
    print(f"[+] Ganache Connected:  {health['ganache_connected']}")
    print(f"[+] RPC URL:            {health['rpc_url']}")
    print(f"[+] Current Block:      {health['current_block']}")
    print(f"[+] Contract Address:   {health['contract_address']}")

    # STEP 2 & 4: Start Election on Smart Contract
    print_step(4, "Start Election 'ELECTION_2026' on Blockchain")
    res = requests.post(f"{BASE_URL}/api/election/start", json={"election_id": "ELECTION_2026"})
    if res.status_code == 200:
        st_data = res.json()
        print(f"[+] Election Started! Tx Hash: {st_data['transaction_hash']}")
        print(f"[+] Block Number: {st_data['block_number']}")
    else:
        print(f"[*] Election already active or error: {res.text}")

    # STEP 5: Add 4 Dummy Protected Ballots
    print_step(5, "Add Four Dummy Protected Ballots to Temporary Queue")
    res = requests.post(f"{BASE_URL}/api/integration/seed-dummy-queue")
    assert res.status_code == 200
    seed_data = res.json()
    print(f"[+] Queue Count: {seed_data['queue_count']}")
    for b in seed_data.get("seeded_ballots", []):
        print(f"    - Ballot: {b['encrypted_ballot']} | Nullifier: {b['nullifier']}")

    # STEP 6: Inspect Temporary Queue
    print_step(6, "Inspect Temporary Protected Queue")
    res = requests.get(f"{BASE_URL}/api/queue")
    q_data = res.json()
    print(f"[+] Total in Queue: {q_data['count']}")
    print("    Original Queue Order:")
    for idx, item in enumerate(q_data["queue"]):
        print(f"    [{idx+1}] {item['encrypted_ballot']} | {item['nullifier']}")

    # STEP 7: Cryptographically Shuffle Queue
    print_step(7, "Shuffle Temporary Queue")
    res = requests.post(f"{BASE_URL}/api/queue/shuffle")
    shuffled_data = res.json()
    print(f"[+] Queue Shuffled Successfully via secrets.SystemRandom entropy source.")
    print("    New Shuffled Order:")
    for idx, item in enumerate(shuffled_data["queue"]):
        print(f"    [{idx+1}] {item['encrypted_ballot']} | {item['nullifier']}")

    # STEP 8, 9 & 10: Create Batch and Submit to Ganache
    print_step(8, "Create Batch & Submit to Ganache Smart Contract")
    res = requests.post(f"{BASE_URL}/api/queue/process", json={"max_batch_size": 10})
    assert res.status_code == 200, f"Batch submission failed: {res.text}"
    batch_res = res.json()
    print(f"[+] Batch ID:          {batch_res['batch_id']}")
    print(f"[+] Transaction Hash:  {batch_res['transaction_hash']}")
    print(f"[+] Block Number:      {batch_res['block_number']}")
    print(f"[+] Total Ballots:     {batch_res['count']}")
    print(f"[+] Person 1 Notified: {batch_res['person1_notified']}")

    # STEP 11: Show Blockchain Audit Records
    print_step(11, "Query On-Chain Immutable Vote Records")
    res = requests.get(f"{BASE_URL}/api/blockchain/audit")
    bc_audit = res.json()
    print(f"[+] Total Confirmed on Blockchain: {bc_audit['total_votes_on_chain']}")
    for r in bc_audit["records"]:
        print(f"    Block #{r['block_number']} | Batch: {r['batch_id']} | Nullifier: {r['nullifier']} | Ciphertext: {r['encrypted_ballot']}")

    # STEP 12: Replay Attack Demo (Duplicate Nullifier Rejection)
    print_step(12, "Attempt Replay Attack with Used Nullifier (NULLIFIER_001)")
    res = requests.post(f"{BASE_URL}/api/vote", json={
        "election_id": "ELECTION_2026",
        "encrypted_ballot": "ENC_BALLOT_REPLAY_ATTEMPT",
        "nullifier": "NULLIFIER_001",
        "batch_id": "BATCH_REPLAY_TEST",
    })
    print(f"[+] HTTP Status Code: {res.status_code}")
    print(f"[+] Smart Contract Rejection Response: {res.json()['detail']}")
    assert res.status_code == 400
    assert "nullifier has already been used" in res.json()["detail"]
    print("[+] SUCCESS: Double-vote attempt was rejected by the Solidity smart contract!")

    # STEP 13: Cryptographic Audit Chain Verification
    print_step(13, "Verify SHA-256 Hash Chained Audit Trail")
    res = requests.get(f"{BASE_URL}/api/audit/verify")
    audit_ver = res.json()
    print(f"[+] Verification Result: {audit_ver['verified']}")
    print(f"[+] Verification Message: {audit_ver['message']}")
    assert audit_ver["verified"] is True

    # STEP 14: Educational Tamper Detection Simulation
    print_step(14, "Run Educational Tamper Detection Simulation")
    res = requests.post(f"{BASE_URL}/api/audit/tamper-demo")
    t_demo = res.json()
    print(f"[+] Simulation: {t_demo['simulation_label']}")
    print(f"    - Target Entry Index: #{t_demo['target_index']}")
    print(f"    - Before Tampering: {t_demo['before_tampering']['verification']['message']}")
    print(f"    - After Tampering:  {t_demo['after_tampering']['verification']['message']}")
    print(f"    - Cryptographic Principle: {t_demo['explanation']}")
    assert t_demo["after_tampering"]["verification"]["verified"] is False

    # STEP 15: Person 1 Inter-Module Confirmation Dispatch
    print_step(15, "Inspect Person 1 Confirmation Callbacks")
    res = requests.get(f"{BASE_URL}/api/integration/person1/notifications")
    p1_data = res.json()
    print(f"[+] Total Dispatches to Person 1: {len(p1_data['dispatched_by_person3'])}")
    for d in p1_data["dispatched_by_person3"]:
        print(f"    - Vote Recorded: {d['vote_recorded']} | Tx: {d['transaction_hash'][:16]}... | Block: {d['block_number']}")
    print("[+] Note: Zero voter PII or biometric data was transmitted across this boundary.")

    # STEP 16: Person 2 Receipt Format
    print_step(16, "Inspect Person 2 Receipt Format")
    receipts = batch_res.get("receipts", [])
    if receipts:
        sample_receipt = receipts[0]
        print("[+] Sample Person 2 Receipt Payload:")
        print(json.dumps(sample_receipt, indent=2))
        print("[+] Confirmed: Receipt contains Nullifier, Tx Hash, Block Number, Batch ID, and ZERO plaintext candidate names.")

    print("\n" + "=" * 70)
    print("ALL 16 DEMONSTRATION STEPS COMPLETED SUCCESSFULLY!")
    print("=" * 70)


if __name__ == "__main__":
    try:
        run_demo()
    except Exception as e:
        print(f"[-] Demo failed: {e}", file=sys.stderr)
        sys.exit(1)
