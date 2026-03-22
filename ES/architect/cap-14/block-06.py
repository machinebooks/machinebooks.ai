# Extraído de: LibroTecnico/cap-14-agentes-orchestrator.md
@dataclass
class SecurityContext:
    """Contexto de seguridad propagado a cada herramienta."""
    user_id: int = 0
    app_code: str = "operations"
    allowed_collections: List[str] = field(default_factory=list)
    is_internal: bool = False      # True si viene del backend inter-servicio
    is_admin: bool = False
    project_id: Optional[int] = None
    client_id: Optional[int] = None

    def can_access_collection(self, collection: str) -> bool:
        """Verifica permisos sobre colecciones RAG."""
        if collection in SYSTEM_ONLY_COLLECTIONS:
            return self.is_internal
        if collection in RESTRICTED_RAG_COLLECTIONS:
            return self.is_internal or self.is_admin
        if self.allowed_collections:
            return collection in self.allowed_collections
        return True  # Colecciones públicas
