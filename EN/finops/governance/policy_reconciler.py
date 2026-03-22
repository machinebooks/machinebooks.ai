# Source: The FinOps Engineer and the Machine -- Chapter 20
# Pattern: Policy reconciler -- merge global + tenant policies

# services/policy_reconciler.py
import yaml
import os
import hashlib
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

POLICIES_PATH = Path(os.environ.get("POLICIES_REPO_PATH", "/app/policies"))


class PolicyCache:
    """In-memory cache with file hash versioning."""

    def __init__(self):
        self._cache: Dict[str, dict] = {}
        self._hashes: Dict[str, str] = {}

    def get(self, path: str) -> Optional[dict]:
        current_hash = self._file_hash(path)
        if self._hashes.get(path) != current_hash:
            self._reload(path)
        return self._cache.get(path)

    def _reload(self, path: str) -> None:
        with open(path, "r", encoding="utf-8") as f:
            self._cache[path] = yaml.safe_load(f)
        self._hashes[path] = self._file_hash(path)
        logger.info(f"Policy reloaded: {path}")

    def _file_hash(self, path: str) -> str:
        with open(path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
