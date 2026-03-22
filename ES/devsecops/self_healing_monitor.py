# Extraído de: LibroDevSecOps/cap-29-futuro-seguridad-autonoma.md
# self_healing_monitor.py — Monitor de salud del pipeline
import anthropic
from datetime import datetime, timedelta

client = anthropic.Anthropic()

def diagnose_pipeline_failure(component: str, error_log: str) -> dict:
    """Usa Claude para diagnosticar fallos del propio pipeline."""
    response = client.messages.create(
        model="claude-haiku-4-5",  # Modelo ligero para diagnóstico rápido
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"""Analiza este fallo del componente {component}
            del pipeline DevSecOps y propón una acción correctiva.

            Error log:
            {error_log}

            Responde con JSON:
            {{"diagnosis": "...", "action": "...",
              "safe_to_auto_fix": true/false,
              "estimated_impact": "none|low|medium|high"}}"""
        }]
    )
    # Parsear respuesta y ejecutar acción si es segura
    return parse_diagnosis(response.content[0].text)

def check_pipeline_health():
    """Monitoriza componentes del pipeline y activa self-healing."""
    components = [
        "semgrep_scanner", "grype_scanner", "trivy_scanner",
        "triage_agent", "remediation_agent", "falco_runtime"
    ]
    for component in components:
        status = get_component_status(component)
        if status.consecutive_failures >= 3:
            diagnosis = diagnose_pipeline_failure(
                component, status.last_error_log
            )
            if diagnosis["safe_to_auto_fix"]:
                apply_auto_fix(component, diagnosis["action"])
                log_self_healing_event(component, diagnosis)
            else:
                escalate_to_human(component, diagnosis)
