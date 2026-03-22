# Extraído de: LibroDevSecOps/cap-19-observabilidad-seguridad.md
# security_metrics_exporter.py
from prometheus_client import (
    Gauge, Histogram, Counter, start_http_server
)
import json
import time
from pathlib import Path
from datetime import datetime, timezone

# --- Métricas de hallazgos ---
open_findings = Gauge(
    "devsecops_findings_open_total",
    "Hallazgos de seguridad abiertos",
    ["tool", "severity", "service"]
)

findings_detected = Counter(
    "devsecops_findings_detected_total",
    "Total de hallazgos detectados",
    ["tool", "severity", "pipeline_stage"]
)

findings_remediated = Counter(
    "devsecops_findings_remediated_total",
    "Hallazgos remediados",
    ["severity", "remediation_type"]  # auto, manual
)

false_positives = Counter(
    "devsecops_false_positives_total",
    "Hallazgos descartados como falsos positivos",
    ["tool", "severity"]
)

# --- Métricas temporales ---
time_to_detect = Histogram(
    "devsecops_mttd_seconds",
    "Tiempo desde introducción hasta detección",
    ["severity"],
    buckets=[60, 300, 900, 3600, 86400, 604800]
)

time_to_remediate = Histogram(
    "devsecops_mttr_seconds",
    "Tiempo desde detección hasta remediación",
    ["severity"],
    buckets=[3600, 86400, 259200, 604800, 2592000]
)

# --- Métricas de cobertura ---
scan_coverage = Gauge(
    "devsecops_scan_coverage_ratio",
    "Ratio de PRs escaneadas sobre total",
    ["scan_type"]  # sast, sca, secret, container
)

scan_duration = Histogram(
    "devsecops_scan_duration_seconds",
    "Duración de cada escaneo",
    ["tool", "pipeline_stage"],
    buckets=[5, 15, 30, 60, 120, 300]
)
