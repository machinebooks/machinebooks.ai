# Extracted from: LibroAISafety/ch-18-rag-security.md
import hashlib
import json
from datetime import datetime, timezone

class RAGIntegrityMonitor:
    """Monitors the integrity of the vector database."""

    def __init__(self, vector_store):
        self.vector_store = vector_store
        self._baseline_hashes: dict[str, str] = {}

    def take_snapshot(self, collection_name: str) -> str:
        """Generates an integrity hash of the collection."""
        collection = self.vector_store.get_collection(collection_name)
        # Get all IDs and content hashes
        all_docs = collection.get(include=["metadatas"])
        content_hashes = sorted([
            m.get("content_hash", "")
            for m in all_docs["metadatas"]
        ])
        snapshot = hashlib.sha256(
            json.dumps(content_hashes).encode()
        ).hexdigest()
        self._baseline_hashes[collection_name] = snapshot
        return snapshot

    def verify_integrity(self, collection_name: str) -> dict:
        """Verifies that the collection has not been modified."""
        baseline = self._baseline_hashes.get(collection_name)
        if not baseline:
            return {"status": "no_baseline",
                    "message": "No prior snapshot"}

        current = self.take_snapshot(collection_name)
        if current != baseline:
            return {
                "status": "MODIFIED",
                "message": f"Collection {collection_name} modified",
                "baseline_hash": baseline,
                "current_hash": current,
                "timestamp": datetime.now(
                    timezone.utc
                ).isoformat(),
            }
        return {"status": "OK",
                "message": "Integrity verified"}
