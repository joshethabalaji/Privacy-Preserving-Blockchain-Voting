"""
Queue package initialization for Person 3 module.
Transparently proxies Python standard library 'queue' members (Queue, LifoQueue, Empty, etc.)
while exporting Person 3 voting queue components (BallotQueue, BatchManager).
"""

import sys
import importlib.util
from pathlib import Path

# 1. Seamlessly proxy standard library queue to avoid shadowing third-party libraries (urllib3, uvicorn)
_stdlib_candidates = [
    Path(sys.base_prefix) / "Lib" / "queue.py",
    Path(sys.prefix) / "Lib" / "queue.py",
]

for _path in _stdlib_candidates:
    if _path.exists():
        try:
            _spec = importlib.util.spec_from_file_location("_stdlib_queue", str(_path))
            _mod = importlib.util.module_from_spec(_spec)
            _spec.loader.exec_module(_mod)
            for _attr in dir(_mod):
                if not _attr.startswith("__"):
                    globals()[_attr] = getattr(_mod, _attr)
            break
        except Exception:
            pass

# 2. Export Person 3 Voting Queue Components
try:
    from ballot_queue import BallotQueue
    from batch_manager import BatchManager
except ImportError:
    from queue.ballot_queue import BallotQueue
    from queue.batch_manager import BatchManager

__all__ = [
    "BallotQueue",
    "BatchManager",
    "Queue",
    "LifoQueue",
    "PriorityQueue",
    "SimpleQueue",
    "Empty",
    "Full",
]
