# Extraído de: LibroDevSecOps/cap-28-caso-compliance.md
import anthropic
import json
from pathlib import Path
from datetime import datetime, timedelta

# Matriz de mapeo control ENS -> artefactos requeridos
ENS_CONTROL_MAP = {
    "op.exp.2": {
        "nombre": "Configuración de seguridad",
        "artefactos_requeridos": [
            "container-report.sarif",
            "config-audit.json"
        ],
        "criterio_cumplimiento": "Sin hallazgos críticos ni altos en configuración"
    },
    "op.exp.3": {
        "nombre": "Gestión de la configuración",
        "artefactos_requeridos": [
            "git-approval-log.json"
        ],
        "criterio_cumplimiento": "100% de merges a main con aprobación"
    },
    "mp.sw.1": {
        "nombre": "Desarrollo de aplicaciones",
        "artefactos_requeridos": [
            "sast-report.sarif",
            "sca-report.sarif",
            "code-review-log.json"
        ],
        "criterio_cumplimiento": "Escaneo SAST+SCA en cada PR, cero críticos abiertos"
    },
    "mp.sw.2": {
        "nombre": "Aceptación y puesta en servicio",
        "artefactos_requeridos": [
            "ci-gate-results.json",
            "test-results.json"
        ],
        "criterio_cumplimiento": "Gates de CI/CD superados, tests pasados"
    },
    # ... 43 controles adicionales con estructura análoga
}

def recopilar_evidencias(bucket_path: str, periodo_dias: int = 90):
    """Recopila artefactos del almacén de evidencias
    para el periodo indicado."""
    evidencias = {}
    fecha_inicio = datetime.now() - timedelta(days=periodo_dias)
    # Listar artefactos en el bucket para el periodo
    # (implementación con boto3 omitida por brevedad)
    return evidencias

def evaluar_control(control_id: str, control_def: dict,
                    evidencias: dict, client: anthropic.Anthropic):
    """Evalúa un control ENS contra las evidencias disponibles."""
    artefactos_encontrados = []
    artefactos_faltantes = []

    for artefacto in control_def["artefactos_requeridos"]:
        if artefacto in evidencias:
            artefactos_encontrados.append({
                "nombre": artefacto,
                "fecha_mas_reciente": evidencias[artefacto]["fecha"],
                "total_ejecuciones": evidencias[artefacto]["count"],
                "resumen": evidencias[artefacto]["resumen"]
            })
        else:
            artefactos_faltantes.append(artefacto)

    # Claude analiza los artefactos y determina cumplimiento
    prompt = f"""Evalúa el cumplimiento del control ENS {control_id}
({control_def['nombre']}).

Criterio de cumplimiento: {control_def['criterio_cumplimiento']}

Artefactos encontrados:
{json.dumps(artefactos_encontrados, indent=2, ensure_ascii=False)}

Artefactos faltantes: {artefactos_faltantes}

Responde en JSON con: estado (conforme/no_conforme/parcial),
justificacion (2-3 frases), evidencias_referenciadas (lista),
acciones_pendientes (lista, vacía si conforme)."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )
    return json.loads(message.content[0].text)
