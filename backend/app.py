"""
FastAPI Main Application (Person 3)
Privacy-Preserving Blockchain & Audit Module for Electronic Voting System.
"""

import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.config import settings
from backend.services.blockchain_service import blockchain_service
from backend.routes import (
    vote_router,
    queue_router,
    audit_router,
    election_router,
    blockchain_router,
    integration_router,
)

BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(
    title="Person 3: Privacy-Preserving Blockchain & Audit Voting Service",
    description=(
        "Standalone module for Local Blockchain (Ganache), Solidity Smart Contract, "
        "Nullifier Verification, Randomized Queue, Batch Processing, SHA-256 Audit Log, "
        "and Integration Callbacks."
    ),
    version="1.0.0",
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(vote_router)
app.include_router(queue_router)
app.include_router(audit_router)
app.include_router(election_router)
app.include_router(blockchain_router)
app.include_router(integration_router)


@app.get("/api/health", tags=["Health"])
def health_check():
    """Returns application and blockchain health status."""
    net_info = blockchain_service.get_network_info()
    status_info = blockchain_service.get_election_status()
    return {
        "status": "ok",
        "service": "person3-blockchain-voting",
        "role": "Person 3 (Blockchain & Audit Module)",
        "ganache_connected": net_info.get("connected", False),
        "rpc_url": net_info.get("rpc_url"),
        "contract_address": net_info.get("contract_address"),
        "current_block": net_info.get("block_number"),
        "election_status": status_info.get("status"),
        "election_id": status_info.get("election_id"),
    }


# Mount frontend static assets
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/", include_in_schema=False)
    def serve_frontend_root():
        return FileResponse(FRONTEND_DIR / "index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host=settings.HOST, port=settings.PORT, reload=True)
