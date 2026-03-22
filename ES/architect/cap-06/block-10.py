# Extraído de: LibroTecnico/cap-06-iam-seguridad.md
@dataclass
class SecurityContext:
    """Contexto de seguridad propagado a cada herramienta del agente.
    Inmutable durante toda la cadena de ejecución."""
    user_id: int = 0
    app_code: str = "operations"          # Aplicación de origen
    allowed_collections: List[str] = field(default_factory=list)
    is_internal: bool = False             # True si viene del backend inter-servicio
    is_admin: bool = False
    project_id: Optional[int] = None      # Scope de proyecto actual
    client_id: Optional[int] = None       # Scope de cliente actual

    def can_access_collection(self, collection: str) -> bool:
        """Verificar acceso a colección RAG — default deny."""
        if collection in SYSTEM_ONLY_COLLECTIONS:
            return self.is_internal
        if collection in RESTRICTED_RAG_COLLECTIONS:
            return self.is_internal or self.is_admin
        if self.allowed_collections:
            return collection in self.allowed_collections
        return False  # Default: denegar acceso

    @classmethod
    def from_headers(cls, headers: Dict[str, str]) -> "SecurityContext":
        """Construir contexto desde cabeceras HTTP del backend."""
        internal_key = os.environ.get("INTERNAL_API_KEY", "")
        is_internal = bool(
            internal_key
            and headers.get("x-internal-api-key") == internal_key
        )
        return cls(
            user_id=int(headers.get("x-user-id", "0")),
            app_code=headers.get("x-app-code", "operations"),
            is_internal=is_internal,
            is_admin=headers.get("x-user-role", "") == "admin",
        )
