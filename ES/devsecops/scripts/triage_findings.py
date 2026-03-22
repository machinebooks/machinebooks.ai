# Extraído de: LibroDevSecOps/cap-01-pipeline-inseguro.md
# scripts/triage_findings.py
"""
Triaje inteligente de hallazgos SAST usando Claude.
Primer prototipo — el agente completo se desarrolla en el Capítulo 9.
"""
import json
import sys
from pathlib import Path
import anthropic

def load_sarif(path: str) -> list[dict]:
    """Carga hallazgos SARIF y extrae los campos relevantes."""
    with open(path) as f:
        sarif = json.load(f)

    findings = []
    for run in sarif.get("runs", []):
        tool_name = run["tool"]["driver"]["name"]
        for result in run.get("results", []):
            location = result["locations"][0]["physicalLocation"]
            file_path = location["artifactLocation"]["uri"]
            region = location.get("region", {})
            findings.append({
                "rule_id": result["ruleId"],
                "message": result["message"]["text"],
                "severity": result.get("level", "warning"),
                "file": file_path,
                "line": region.get("startLine", 0),
                "tool": tool_name,
            })
    return findings


def triage_finding(client: anthropic.Anthropic, finding: dict,
                   code_context: str) -> dict:
    """Envía un hallazgo a Claude para triaje con contexto de código."""
    prompt = f"""Eres un analista de seguridad experto. Analiza este hallazgo
SAST y determina si es un verdadero positivo o un falso positivo.

## Hallazgo
- Regla: {finding['rule_id']}
- Mensaje: {finding['message']}
- Severidad reportada: {finding['severity']}
- Fichero: {finding['file']}
- Línea: {finding['line']}

## Código fuente (contexto)
