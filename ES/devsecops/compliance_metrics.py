# Extraído de: LibroDevSecOps/cap-28-caso-compliance.md
# compliance_metrics.py — Exportador de métricas para Prometheus
from prometheus_client import Gauge, start_http_server
import boto3
from datetime import datetime, timedelta

# Métricas de compliance
compliance_controles_conformes = Gauge(
    'ens_controles_conformes',
    'Número de controles ENS en estado conforme'
)
compliance_controles_parciales = Gauge(
    'ens_controles_parciales',
    'Número de controles ENS parcialmente conformes'
)
compliance_controles_no_conformes = Gauge(
    'ens_controles_no_conformes',
    'Número de controles ENS no conformes'
)
compliance_evidencia_antiguedad_dias = Gauge(
    'ens_evidencia_antiguedad_max_dias',
    'Antigüedad en días de la evidencia más antigua',
    ['control_id']
)
compliance_cobertura_pipeline = Gauge(
    'ens_cobertura_pipeline_pct',
    'Porcentaje de PRs con pipeline completo'
)

def actualizar_metricas():
    """Consulta el almacén de evidencias y actualiza métricas."""
    # Leer último informe de compliance
    resultados = cargar_ultimo_informe()

    conformes = sum(
        1 for r in resultados.values()
        if r["estado"] == "conforme"
    )
    parciales = sum(
        1 for r in resultados.values()
        if r["estado"] == "parcial"
    )
    no_conformes = sum(
        1 for r in resultados.values()
        if r["estado"] == "no_conforme"
    )

    compliance_controles_conformes.set(conformes)
    compliance_controles_parciales.set(parciales)
    compliance_controles_no_conformes.set(no_conformes)

    # Calcular antigüedad de evidencias por control
    for control_id, datos in resultados.items():
        if "fecha_ultima_evidencia" in datos:
            dias = (datetime.now() - datetime.fromisoformat(
                datos["fecha_ultima_evidencia"]
            )).days
            compliance_evidencia_antiguedad_dias.labels(
                control_id=control_id
            ).set(dias)
