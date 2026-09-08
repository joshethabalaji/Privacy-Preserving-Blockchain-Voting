"""
Routes package initialization.
"""
from backend.routes.vote_routes import router as vote_router
from backend.routes.queue_routes import router as queue_router
from backend.routes.audit_routes import router as audit_router
from backend.routes.election_routes import router as election_router
from backend.routes.blockchain_routes import router as blockchain_router
from backend.routes.integration_routes import router as integration_router

__all__ = [
    "vote_router",
    "queue_router",
    "audit_router",
    "election_router",
    "blockchain_router",
    "integration_router",
]
