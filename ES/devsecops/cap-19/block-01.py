# Extraído de: LibroDevSecOps/cap-19-observabilidad-seguridad.md
def process_semgrep_results(results_path: str, service: str):
    """Procesa un fichero de resultados Semgrep y actualiza métricas."""
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
        # Registra detección
        findings_detected.labels(
            tool="semgrep",
            severity=severity,
            pipeline_stage="commit"
        ).inc()

        # Actualiza hallazgos abiertos
        open_findings.labels(
            tool="semgrep",
            severity=severity,
            service=service
        ).inc()

        # Calcula MTTD si hay timestamp de commit
        commit_ts = result.get("extra", {}).get("commit_timestamp")
        if commit_ts:
            detect_delta = (
                datetime.now(timezone.utc)
                - datetime.fromisoformat(commit_ts)
            ).total_seconds()
            time_to_detect.labels(severity=severity).observe(
                detect_delta
            )
