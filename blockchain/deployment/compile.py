"""
Solidity Contract Compiler Script
Compiles Voting.sol and exports ABI and Bytecode to blockchain/abi/Voting.json.
"""

import json
import os
import sys
from pathlib import Path
import solcx

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONTRACT_PATH = BASE_DIR / "blockchain" / "contracts" / "Voting.sol"
ABI_OUTPUT_DIR = BASE_DIR / "blockchain" / "abi"
ABI_OUTPUT_FILE = ABI_OUTPUT_DIR / "Voting.json"

SOLC_VERSION = "0.8.20"


def compile_contract():
    print(f"[*] Ensuring solc v{SOLC_VERSION} is installed...")
    installed_versions = [str(v) for v in solcx.get_installed_solc_versions()]
    if SOLC_VERSION not in installed_versions:
        print(f"[*] Installing solc v{SOLC_VERSION}...")
        solcx.install_solc(SOLC_VERSION)
    solcx.set_solc_version(SOLC_VERSION)

    print(f"[*] Compiling contract: {CONTRACT_PATH}")
    if not CONTRACT_PATH.exists():
        raise FileNotFoundError(f"Contract file not found at {CONTRACT_PATH}")

    with open(CONTRACT_PATH, "r", encoding="utf-8") as f:
        contract_source = f.read()

    compiled_sol = solcx.compile_standard(
        {
            "language": "Solidity",
            "sources": {"Voting.sol": {"content": contract_source}},
            "settings": {
                "optimizer": {"enabled": True, "runs": 200},
                "outputSelection": {
                    "*": {
                        "*": [
                            "abi",
                            "metadata",
                            "evm.bytecode",
                            "evm.bytecode.sourceMap",
                        ]
                    }
                },
            },
        },
        solc_version=SOLC_VERSION,
    )

    contract_data = compiled_sol["contracts"]["Voting.sol"]["Voting"]
    abi = contract_data["abi"]
    bytecode = contract_data["evm"]["bytecode"]["object"]

    ABI_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(ABI_OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump({"contractName": "Voting", "abi": abi, "bytecode": bytecode}, f, indent=2)

    print(f"[+] Compilation successful! Output saved to: {ABI_OUTPUT_FILE}")
    return abi, bytecode


if __name__ == "__main__":
    try:
        compile_contract()
    except Exception as e:
        print(f"[-] Compilation error: {e}", file=sys.stderr)
        sys.exit(1)
