# Extraído de: LibroDevSecOps/cap-08-orquestacion-pipeline.md
# scripts/weekly_security_report.py
"""
Agente Claude que genera un informe semanal de seguridad
a partir de los resultados acumulados del pipeline.
"""
import json
import anthropic
from datetime import datetime, timedelta

def collect_weekly_findings() -> list[dict]:
    """
    Recopila hallazgos de la última semana.
    En producción, consulta la API de GitHub Actions para
    descargar artefactos de ejecuciones recientes.
    """
    # Simplificado: en producción usar
    # gh api /repos/{owner}/{repo}/actions/artifacts
    findings_dir = "reports/weekly/"
    # ... lógica de recopilación ...
    return []  # Placeholder: retorna hallazgos agregados

def generate_report(findings: list[dict]) -> str:
    """Genera el informe semanal con Claude."""
    client = anthropic.Anthropic()

    # Prepara el contexto para Claude
    summary = {
        "period": (
            f"{(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')}"
            f" a {datetime.now().strftime('%Y-%m-%d')}"
        ),
        "total_findings": len(findings),
        "blocked_prs": sum(
            1 for f in findings if f.get("gate") == "block"
        ),
        "warned_prs": sum(
            1 for f in findings if f.get("gate") == "warn"
        ),
        "passed_prs": sum(
            1 for f in findings if f.get("gate") == "pass"
        ),
        "top_cves": _extract_top_cves(findings),
        "recurring_patterns": _extract_patterns(findings),
    }

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=(
            "Eres un analista de seguridad DevSecOps. Genera un informe "
            "semanal conciso en español para el security lead. "
            "Estructura: resumen ejecutivo (3 líneas), métricas clave "
            "(tabla), hallazgos que requieren atención (lista priorizada), "
            "tendencias respecto a semanas anteriores, recomendaciones "
            "accionables (máximo 3). Tono: directo, sin alarmismo."
        ),
        messages=[{
            "role": "user",
            "content": (
                f"Datos del pipeline de seguridad:\n"
                f"