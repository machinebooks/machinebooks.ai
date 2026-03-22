# Extraído de: LibroCISO/cap-24-calidad-ia.md
import numpy as np
from typing import List, Tuple

def calculate_psi(baseline: List[float], current: List[float],
                  n_bins: int = 10) -> float:
    """Calcula Population Stability Index entre dos distribuciones.

    PSI < 0.10: distribución estable, sin drift significativo.
    PSI 0.10-0.25: drift moderado, investigar causa.
    PSI > 0.25: drift significativo, acción requerida.

    En nuestro contexto, baseline son los tokens/latencias del primer
    mes de producción, y current son los del período actual.
    Un PSI alto puede indicar:
    - Cambio en el tipo de documentos que procesan los usuarios
    - Actualización silenciosa del modelo por el proveedor
    - Cambio en los patrones de uso (más consultas complejas)
    """
    # Crear bins a partir de la distribución baseline
    breakpoints = np.percentile(baseline,
                                np.linspace(0, 100, n_bins + 1))
    breakpoints = np.unique(breakpoints)  # Eliminar duplicados

    # Calcular proporciones en cada bin
    baseline_counts = np.histogram(baseline, bins=breakpoints)[0]
    current_counts = np.histogram(current, bins=breakpoints)[0]

    # Normalizar a proporciones (con suavizado para evitar log(0))
    eps = 1e-4
    baseline_pct = (baseline_counts + eps) / (sum(baseline_counts) + eps * len(baseline_counts))
    current_pct = (current_counts + eps) / (sum(current_counts) + eps * len(current_counts))

    # Calcular PSI
    psi = np.sum(
        (current_pct - baseline_pct) * np.log(current_pct / baseline_pct)
    )

    return round(float(psi), 6)


def detect_drift_for_service(service_type: str,
                             period_days: int = 30) -> dict:
    """Detecta drift para un servicio IA comparando
    distribuciones de tokens y latencia contra la baseline.

    La baseline se establece con los datos del primer mes
    de producción y se puede recalibrar manualmente desde
    el panel de administración.
    """
    from app.database import db_session
    from app.models import LLMUsageLog, AIBaselineSnapshot
    from datetime import datetime, timedelta

    # Obtener baseline guardada
    baseline_snap = db_session.query(AIBaselineSnapshot).filter_by(
        service_type=service_type,
        metric_name='token_distribution',
        is_active=True,
    ).first()

    if not baseline_snap:
        return {
            'status': 'no_baseline',
            'message': 'No hay baseline establecida para este servicio.'
                       ' Ejecute calibración desde Admin > IA > Baselines.'
        }

    # Obtener datos del período actual
    cutoff = datetime.utcnow() - timedelta(days=period_days)
    current_logs = db_session.query(LLMUsageLog).filter(
        LLMUsageLog.service_type == service_type,
        LLMUsageLog.created_at >= cutoff,
        LLMUsageLog.success == True,
    ).all()

    if len(current_logs) < 30:
        return {
            'status': 'insufficient_data',
            'sample_size': len(current_logs),
            'minimum_required': 30,
        }

    # Calcular PSI para tokens totales
    baseline_tokens = baseline_snap.distribution_values  # List[float]
    current_tokens = [log.total_tokens for log in current_logs]
    psi_tokens = calculate_psi(baseline_tokens, current_tokens)

    # Calcular PSI para latencia
    baseline_latency = baseline_snap.latency_distribution
    current_latency = [log.latency_ms for log in current_logs
                       if log.latency_ms]
    psi_latency = calculate_psi(baseline_latency, current_latency) \
        if baseline_latency and current_latency else None

    # Interpretar resultado
    if psi_tokens > 0.25:
        severity = 'critical'
        action = 'Drift significativo detectado. Revisar cambios en el ' \
                 'modelo del proveedor y patrones de uso.'
    elif psi_tokens > 0.10:
        severity = 'warning'
        action = 'Drift moderado. Monitorizar evolución en próximos días.'
    else:
        severity = 'normal'
        action = 'Distribución estable. Sin acción requerida.'

    return {
        'service_type': service_type,
        'psi_tokens': psi_tokens,
        'psi_latency': psi_latency,
        'severity': severity,
        'action': action,
        'sample_size': len(current_logs),
        'baseline_size': len(baseline_tokens),
        'period_days': period_days,
    }
