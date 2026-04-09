# Extraido de: LibroAISafety/cap-18-rag-seguridad.md
import hashlib
import json
from datetime import datetime, timezone

class RAGIntegrityMonitor:
    """Monitoriza la integridad de la base vectorial."""

    def __init__(self, vector_store):
        self.vector_store = vector_store
        self._baseline_hashes: dict[str, str] = {}

    def take_snapshot(self, collection_name: str) -> str:
        """Genera un hash de integridad de la colección."""
        collection = self.vector_store.get_collection(collection_name)
        # Obtener todos los IDs y hashes de contenido
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
        """Verifica que la colección no ha sido modificada."""
        baseline = self._baseline_hashes.get(collection_name)
        if not baseline:
            return {"status": "no_baseline",
                    "message": "Sin snapshot previo"}

        current = self.take_snapshot(collection_name)
        if current != baseline:
            return {
                "status": "MODIFIED",
                "message": f"Colección {collection_name} modificada",
                "baseline_hash": baseline,
                "current_hash": current,
                "timestamp": datetime.now(
                    timezone.utc
                ).isoformat(),
            }
        return {"status": "OK",
                "message": "Integridad verificada"}
