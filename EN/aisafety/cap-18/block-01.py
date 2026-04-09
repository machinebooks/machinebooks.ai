# Extracted from: LibroAISafety/ch-18-rag-security.md
@dataclass
class UserContext:
    """Security context of the querying user."""
    user_id: str
    roles: list[str]
    department: str
    max_classification: DocClassification

class SecureRAGQuery:
    """RAG query with per-user access control."""

    def __init__(self, vector_store, embedding_model):
        self.vector_store = vector_store
        self.embedding_model = embedding_model

    def query(self, question: str, user: UserContext,
              top_k: int = 5) -> list[dict]:
        """Retrieves documents respecting user permissions."""
        query_embedding = self.embedding_model.encode(question)

        # Determine collections accessible to this user
        accessible = self._get_accessible_collections(user)

        all_results = []
        for collection_name in accessible:
            collection = self.vector_store.get_collection(
                collection_name
            )
            # Filter by user roles
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where={
                    "$or": [
                        {"allowed_roles": {"$contains": role}}
                        for role in user.roles
                    ]
                }
            )
            all_results.extend(self._format_results(
                results, collection_name
            ))

        # Sort by relevance and take top_k
        all_results.sort(key=lambda x: x["score"], reverse=True)
        return all_results[:top_k]

    def _get_accessible_collections(
            self, user: UserContext) -> list[str]:
        """Returns the collections the user can query."""
        classification_order = [
            DocClassification.PUBLIC,
            DocClassification.INTERNAL,
            DocClassification.CONFIDENTIAL,
            DocClassification.RESTRICTED,
        ]
        max_idx = classification_order.index(
            user.max_classification
        )
        accessible_classifications = classification_order[:max_idx + 1]

        collection_map = {
            DocClassification.PUBLIC: "docs_public",
            DocClassification.INTERNAL: "docs_internal",
            DocClassification.CONFIDENTIAL: "docs_confidential",
            DocClassification.RESTRICTED: "docs_restricted",
        }
        return [collection_map[c] for c in accessible_classifications]

    def _format_results(self, raw_results: dict,
                        collection: str) -> list[dict]:
        """Formats results with security provenance."""
        formatted = []
        if raw_results and raw_results.get("documents"):
            for i, doc in enumerate(raw_results["documents"][0]):
                formatted.append({
                    "text": doc,
                    "score": 1 - raw_results["distances"][0][i],
                    "collection": collection,
                    "metadata": raw_results["metadatas"][0][i],
                })
        return formatted
