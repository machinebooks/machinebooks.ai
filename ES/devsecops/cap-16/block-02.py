# Extraído de: LibroDevSecOps/cap-16-data-poisoning-rag.md
from functools import wraps
from dataclasses import dataclass
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchAny

@dataclass
class UserContext:
    user_id: str
    groups: list[str]
    clearance: ClassificationLevel

def require_access_control(func):
    """Decorador que inyecta filtro de acceso en consultas RAG."""
    @wraps(func)
    def wrapper(self, query: str, user: UserContext, **kwargs):
        # Determinar niveles accesibles según clearance del usuario
        clearance_hierarchy = {
            ClassificationLevel.PUBLIC: [
                ClassificationLevel.PUBLIC.value
            ],
            ClassificationLevel.INTERNAL: [
                ClassificationLevel.PUBLIC.value,
                ClassificationLevel.INTERNAL.value
            ],
            ClassificationLevel.CONFIDENTIAL: [
                ClassificationLevel.PUBLIC.value,
                ClassificationLevel.INTERNAL.value,
                ClassificationLevel.CONFIDENTIAL.value
            ],
            ClassificationLevel.RESTRICTED: [
                ClassificationLevel.PUBLIC.value,
                ClassificationLevel.INTERNAL.value,
                ClassificationLevel.CONFIDENTIAL.value,
                ClassificationLevel.RESTRICTED.value
            ],
        }
        allowed_levels = clearance_hierarchy[user.clearance]

        # Construir filtro: nivel de clasificación Y grupo autorizado
        access_filter = Filter(must=[
            FieldCondition(
                key="classification",
                match=MatchAny(any=allowed_levels)
            ),
            FieldCondition(
                key="authorized_groups",
                match=MatchAny(any=user.groups)
            ),
        ])

        # Inyectar filtro en los kwargs antes de ejecutar la consulta
        kwargs["query_filter"] = access_filter
        kwargs["user_context"] = user

        return func(self, query, user, **kwargs)
    return wrapper

class SecureRAGRetriever:
    """Retriever con control de acceso pre-filtrado."""

    def __init__(self, qdrant_url: str, collection: str):
        self.client = QdrantClient(url=qdrant_url)
        self.collection = collection

    @require_access_control
    def retrieve(
        self, query: str, user: UserContext, top_k: int = 5,
        query_filter: Filter = None, **kwargs
    ) -> list[dict]:
        """Busca fragmentos relevantes respetando permisos."""
        # El filtro se aplica ANTES del cálculo de similitud
        results = self.client.search(
            collection_name=self.collection,
            query_vector=self._embed(query),
            query_filter=query_filter,
            limit=top_k,
        )

        # Registrar consulta para auditoría
        self._audit_log(user, query, len(results))

        return [
            {
                "text": hit.payload["text"],
                "source": hit.payload["source"],
                "classification": hit.payload["classification"],
                "score": hit.score,
            }
            for hit in results
        ]

    def _embed(self, text: str) -> list[float]:
        """Genera embedding para la consulta (simplificado)."""
        # En producción: llamada a modelo de embeddings
        # Ejemplo con Anthropic o modelo local
        pass

    def _audit_log(
        self, user: UserContext, query: str, results_count: int
    ):
        """Registra cada consulta para trazabilidad."""
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user_id": user.user_id,
            "clearance": user.clearance.value,
            "groups": user.groups,
            "query_hash": hashlib.sha256(
                query.encode()
            ).hexdigest()[:16],
            "results_returned": results_count,
        }
        # En producción: enviar a sistema de logging centralizado
        print(json.dumps(log_entry))
