# Extraído de: LibroDevSecOps/cap-02-anatomia-vulnerabilidad.md
import anthropic
import json

client = anthropic.Anthropic()

def triage_sast_finding(finding: dict, service_context: dict) -> dict:
    """
    Analiza un hallazgo SAST con contexto de servicio.

    Args:
        finding: hallazgo de Semgrep en formato JSON
        service_context: metadata del servicio (exposición, datos, controles)
    """
    prompt = f"""Eres un analista de seguridad experto. Analiza este hallazgo SAST
y clasifícalo según el riesgo real para la organización.

## Hallazgo SAST
- Regla: {finding["check_id"]}
- Severidad técnica: {finding["extra"]["severity"]}
- CWE: {finding["extra"]["metadata"].get("cwe", "N/A")}
- Fichero: {finding["path"]}
- Línea: {finding["start"]["line"]}
- Código afectado:
