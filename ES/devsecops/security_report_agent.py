# Extraído de: LibroDevSecOps/cap-19-observabilidad-seguridad.md
# security_report_agent.py
import anthropic
import requests
from datetime import datetime, timedelta

client = anthropic.Anthropic()
PROMETHEUS_URL = "http://prometheus:9090/api/v1"


def query_prometheus(promql: str, time_range: str = "7d") -> dict:
    """Ejecuta una query PromQL y devuelve el resultado."""
    response = requests.get(
        f"{PROMETHEUS_URL}/query",
        params={"query": promql},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()["data"]["result"]


def collect_weekly_metrics() -> dict:
    """Recoge todas las métricas de seguridad de la última semana."""
    metrics = {}

    # Hallazgos abiertos por severidad
    results = query_prometheus(
        'sum by (severity) (devsecops_findings_open_total)'
    )
    metrics["open_findings"] = {
        r["metric"]["severity"]: int(r["value"][1])
        for r in results
    }

    # MTTR medio por severidad (en horas)
    for sev in ["critical", "high", "medium"]:
        result = query_prometheus(
            f'histogram_quantile(0.50, rate('
            f'devsecops_mttr_seconds_bucket{{severity="{sev}"}}[7d]))'
        )
        if result:
            hours = float(result[0]["value"][1]) / 3600
            metrics.setdefault("mttr_hours", {})[sev] = round(
                hours, 1
            )

    # Fix rate semanal
    remediated = query_prometheus(
        'sum(increase(devsecops_findings_remediated_total[7d]))'
    )
    detected = query_prometheus(
        'sum(increase(devsecops_findings_detected_total[7d]))'
    )
    if remediated and detected:
        rem_val = float(remediated[0]["value"][1])
        det_val = float(detected[0]["value"][1])
        metrics["fix_rate"] = round(
            (rem_val / det_val * 100) if det_val > 0 else 0, 1
        )

    # Cobertura de escaneo
    coverage = query_prometheus(
        'avg(devsecops_scan_coverage_ratio)'
    )
    if coverage:
        metrics["scan_coverage"] = round(
            float(coverage[0]["value"][1]) * 100, 1
        )

    # Tasa de falsos positivos
    fp = query_prometheus(
        'sum(increase(devsecops_false_positives_total[7d]))'
    )
    total = query_prometheus(
        'sum(increase(devsecops_findings_detected_total[7d]))'
    )
    if fp and total:
        fp_val = float(fp[0]["value"][1])
        tot_val = float(total[0]["value"][1])
        metrics["false_positive_rate"] = round(
            (fp_val / tot_val * 100) if tot_val > 0 else 0, 1
        )

    return metrics
