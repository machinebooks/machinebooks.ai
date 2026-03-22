# Extraído de: LibroDevSecOps/cap-09-agente-triaje.md
from functools import lru_cache

@lru_cache(maxsize=256)
def cached_service_exposure(service_name: str) -> dict:
    """Caché de exposición de servicios — evita consultas
    repetidas al inventario durante un ciclo de triaje."""
    return check_service_exposure(service_name)

@lru_cache(maxsize=512)
def cached_cve_query(cve_id: str) -> dict:
    """Caché de consultas CVE — evita llamadas repetidas
    a NVD/OSV para la misma vulnerabilidad."""
    return query_cve_database(cve_id)
