# Extraído de: LibroCyberrange/cap-24-seguridad-plataforma.md
# Schema de validación para filtros de auditoría
# Fichero: cyber-range-builder/backend/schemas.py

class AuditLogFilter(BaseModel):
    """Filtros para búsqueda de logs de auditoría.
    Pydantic valida tipos, rangos y opciones permitidas
    ANTES de que la query llegue a la base de datos."""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    event_types: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    severities: Optional[List[str]] = None
    user_ids: Optional[List[int]] = None
    usernames: Optional[List[str]] = None
    ip_addresses: Optional[List[str]] = None
    actions: Optional[List[str]] = None
    resource_types: Optional[List[str]] = None
    modules: Optional[List[str]] = None
    statuses: Optional[List[str]] = None
    review_statuses: Optional[List[str]] = None
    correlation_id: Optional[str] = None
    search_text: Optional[str] = None
    tags: Optional[List[str]] = None

class AuditExportRequest(BaseModel):
    format: str = 'csv'              # csv, json
    filters: Optional[AuditLogFilter] = None
    include_details: bool = False
    max_records: int = 10000         # Límite configurable por el usuario
