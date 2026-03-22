# Extraído de: LibroTecnico/cap-03-ecosistema-claude.md
@dataclass
class SecurityContext:
    """Contexto de seguridad propagado a cada tool.
    Se crea una vez al inicio de la petición HTTP y se pasa
    a través de todas las capas sin necesidad de re-verificar permisos."""
    user_id: int = 0
    app_code: str = "operations"
    allowed_collections: List[str] = field(default_factory=list)
    is_internal: bool = False
    is_admin: bool = False
    project_id: Optional[int] = None
    client_id: Optional[int] = None

    def can_access_collection(self, collection: str) -> bool:
        """Verificar acceso a colección RAG.
        Principio: default-DENY — si no hay regla explícita, se deniega."""
        if collection in SYSTEM_ONLY_COLLECTIONS:
            return self.is_internal
        if collection in RESTRICTED_RAG_COLLECTIONS:
            return self.is_internal or self.is_admin
        if self.allowed_collections:
            return collection in self.allowed_collections
        if collection in PUBLIC_COLLECTIONS:
            return True  # Solo colecciones explícitamente públicas
        return False  # Default: denegar acceso
