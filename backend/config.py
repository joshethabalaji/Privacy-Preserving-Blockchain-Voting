"""
Configuration settings for Person 3 Backend.
"""

import sys
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
QUEUE_DIR = BASE_DIR / "queue"
AUDIT_DIR = BASE_DIR / "audit"

for p in [str(BASE_DIR), str(QUEUE_DIR), str(AUDIT_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)


class Settings:
    BASE_DIR = BASE_DIR
    GANACHE_RPC_URL = os.getenv("GANACHE_RPC_URL", "http://127.0.0.1:7545")
    CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS", "")
    BLOCKCHAIN_ACCOUNT = os.getenv("BLOCKCHAIN_ACCOUNT", "")
    PRIVATE_KEY = os.getenv("PRIVATE_KEY", "")
    DEFAULT_ELECTION_ID = os.getenv("DEFAULT_ELECTION_ID", "ELECTION_2026")
    MOCK_PERSON1_URL = os.getenv("MOCK_PERSON1_URL", "http://127.0.0.1:8000/api/integration/person1/vote-confirmed")
    HOST = os.getenv("HOST", "127.0.0.1")
    PORT = int(os.getenv("PORT", "8000"))
    ABI_FILE = BASE_DIR / "blockchain" / "abi" / "Voting.json"


settings = Settings()
