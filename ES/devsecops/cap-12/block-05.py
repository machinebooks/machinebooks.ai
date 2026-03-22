# Extraído de: LibroDevSecOps/cap-12-dast-inteligente.md
import subprocess
import json
import time
from pathlib import Path

def run_zap_scan(
    plan_path: str,
    target_url: str,
    results_dir: str = "/tmp/zap-results",
) -> dict:
    """Ejecuta OWASP ZAP con el plan de automatización generado."""
    Path(results_dir).mkdir(parents=True, exist_ok=True)

    # Ejecutar ZAP en modo headless con el plan de automatización
    cmd = [
        "docker", "run", "--rm",
        "-v", f"{plan_path}:/zap/plan.yaml:ro",
        "-v", f"{results_dir}:/zap/results",
        "--network", "host",
        "ghcr.io/zaproxy/zaproxy:stable",
        "zap.sh", "-cmd",
        "-autorun", "/zap/plan.yaml",
    ]

    start_time = time.time()
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
    elapsed = time.time() - start_time

    # Leer resultados
    report_path = Path(results_dir) / "zap-report.json"
    if report_path.exists():
        with open(report_path) as f:
            zap_results = json.load(f)
    else:
        zap_results = {"error": "No se generó informe", "stderr": result.stderr}

    return {
        "results": zap_results,
        "exit_code": result.returncode,
        "elapsed_seconds": round(elapsed, 1),
        "stdout_summary": result.stdout[-500:] if result.stdout else "",
    }
