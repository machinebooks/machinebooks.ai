# Extraido de: LibroAISafety/cap-18-rag-seguridad.md
@dataclass
class UserContext:
    """Contexto de seguridad del usuario que consulta."""
    user_id: str
    roles: list[str]
    department: str
    max_classification: DocClassification

class SecureRAGQuery:
    """Consulta RAG con control de acceso por usuario."""

    def __init__(self, vector_store, embedding_model):
        self.vector_store = vector_store
        self.embedding_model = embedding_model

    def query(self, question: str, user: UserContext,
              top_k: int = 5) -> list[dict]:
        """Recupera documentos respetando los permisos del usuario."""
        query_embedding = self.embedding_model.encode(question)

        # Determinar colecciones accesibles para este usuario
        accessible = self._get_accessible_collections(user)

        all_results = []
        for collection_name in accessible:
            collection = self.vector_store.get_collection(
                collection_name
            )
            # Filtrar por roles del usuario
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

        # Ordenar por relevancia y tomar top_k
        all_results.sort(key=lambda x: x["score"], reverse=True)
        return all_results[:top_k]

    def _get_accessible_collections(
            self, user: UserContext) -> list[str]:
        """Retorna las colecciones que el usuario puede consultar."""
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
        """Formatea resultados con procedencia de seguridad."""
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
