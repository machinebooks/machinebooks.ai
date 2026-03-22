# Extraído de: LibroDevSecOps/cap-20-respuesta-incidentes.md
from dataclasses import dataclass, field
from enum import Enum

class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class SecurityAlert:
    source: str            # falco, pipeline, waf, ids
    timestamp: str         # ISO 8601
    severity: Severity
    description: str
    container_id: str | None = None
    service_name: str | None = None
    cve_id: str | None = None
    raw_data: dict = field(default_factory=dict)

@dataclass
class CorrelatedIncident:
    incident_id: str
    alerts: list[SecurityAlert]
    probable_vector: str        # Hipótesis del vector de ataque
    affected_services: list[str]
    timeline: list[dict]        # Eventos ordenados cronológicamente
    severity: Severity
    recommended_actions: list[str]

def correlate_alerts(
    alerts: list[SecurityAlert],
    time_window_minutes: int = 15
) -> list[CorrelatedIncident]:
    """Agrupa alertas por proximidad temporal y servicios afectados."""
    # Ordenar por timestamp
    sorted_alerts = sorted(alerts, key=lambda a: a.timestamp)

    # Agrupación por ventana temporal y servicio
    clusters: list[list[SecurityAlert]] = []
    current_cluster: list[SecurityAlert] = []

    for alert in sorted_alerts:
        if not current_cluster:
            current_cluster.append(alert)
            continue
        # Si la alerta cae dentro de la ventana, la añadimos al cluster
        time_diff = _minutes_between(current_cluster[-1].timestamp, alert.timestamp)
        if time_diff <= time_window_minutes:
            current_cluster.append(alert)
        else:
            clusters.append(current_cluster)
            current_cluster = [alert]

    if current_cluster:
        clusters.append(current_cluster)

    # Convertir clusters en incidentes correlados
    incidents = []
    for i, cluster in enumerate(clusters):
        affected = list({a.service_name for a in cluster if a.service_name})
        max_sev = max(cluster, key=lambda a: _severity_rank(a.severity))
        incidents.append(CorrelatedIncident(
            incident_id=f"INC-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{i+1:03d}",
            alerts=cluster,
            probable_vector="pending_analysis",  # Claude lo enriquecerá
            affected_services=affected,
            timeline=[{"time": a.timestamp, "event": a.description} for a in cluster],
            severity=max_sev.severity,
            recommended_actions=[]  # Claude las generará
        ))
    return incidents
