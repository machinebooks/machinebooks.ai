# Source: The DevSecOps and the Machine -- Chapter 19
# Pattern: Prometheus metrics exporter for security pipeline

# security_metrics_exporter.py
from prometheus_client import (
    Gauge, Histogram, Counter, start_http_server
)
import json
import time
from pathlib import Path
from datetime import datetime, timezone

# --- Finding metrics ---
open_findings = Gauge(
    "devsecops_findings_open_total",
    "Open security findings",
    ["tool", "severity", "service"]
)

findings_detected = Counter(
    "devsecops_findings_detected_total",
    "Total findings detected",
    ["tool", "severity", "pipeline_stage"]
)

findings_remediated = Counter(
    "devsecops_findings_remediated_total",
    "Remediated findings",
    ["severity", "remediation_type"]  # auto, manual
)

false_positives = Counter(
    "devsecops_false_positives_total",
    "Findings dismissed as false positives",
    ["tool", "severity"]
)

# --- Temporal metrics ---
time_to_detect = Histogram(
    "devsecops_mttd_seconds",
    "Time from introduction to detection",
    ["severity"],
    buckets=[60, 300, 900, 3600, 86400, 604800]
)

time_to_remediate = Histogram(
    "devsecops_mttr_seconds",
    "Time from detection to remediation",
    ["severity"],
    buckets=[3600, 86400, 259200, 604800, 2592000]
)

# --- Coverage metrics ---
scan_coverage = Gauge(
    "devsecops_scan_coverage_ratio",
    "Ratio of scanned PRs over total",
    ["scan_type"]  # sast, sca, secret, container
)

scan_duration = Histogram(
    "devsecops_scan_duration_seconds",
    "Duration of each scan",
    ["tool", "pipeline_stage"],
    buckets=[5, 15, 30, 60, 120, 300]
)

def process_semgrep_results(results_path: str, service: str):
    """Process a Semgrep results file and update metrics."""
    with open(results_path) as f:
        data = json.load(f)

    severity_map = {
        "ERROR": "critical",
        "WARNING": "high",
        "INFO": "medium"
    }

    for result in data.get("results", []):
        severity = severity_map.get(
            result.get("extra", {}).get("severity", "INFO"),
            "low"
        )
        # Record detection
        findings_detected.labels(
            tool="semgrep",
            severity=severity,
            pipeline_stage="commit"
        ).inc()

        # Update open findings
        open_findings.labels(
            tool="semgrep",
            severity=severity,
            service=service
        ).inc()

        # Calculate MTTD if commit timestamp is available
        commit_ts = result.get("extra", {}).get("commit_timestamp")
        if commit_ts:
            detect_delta = (
                datetime.now(timezone.utc)
                - datetime.fromisoformat(commit_ts)
            ).total_seconds()
            time_to_detect.labels(severity=severity).observe(
                detect_delta
            )