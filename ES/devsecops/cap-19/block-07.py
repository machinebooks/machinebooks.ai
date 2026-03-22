# Extraído de: LibroDevSecOps/cap-19-observabilidad-seguridad.md
def generate_security_report(
    metrics: dict,
    audience: str,  # "engineer", "lead", "ciso"
    previous_metrics: dict | None = None,
) -> str:
    """Genera informe de seguridad semanal con Claude."""

    # Calcula deltas si hay métricas anteriores
    deltas = {}
    if previous_metrics:
        for key in ["fix_rate", "scan_coverage", "false_positive_rate"]:
            if key in metrics and key in previous_metrics:
                deltas[key] = metrics[key] - previous_metrics[key]

    audience_prompts = {
        "engineer": (
            "Genera un informe breve para ingenieros de desarrollo. "
            "Enfócate en hallazgos abiertos que requieren acción, "
            "los servicios más afectados y los fixes pendientes. "
            "Tono directo, accionable. Máximo 300 palabras. "
            "Incluye una lista priorizada de acciones."
        ),
        "lead": (
            "Genera un informe semanal para el security lead. "
            "Analiza tendencias de MTTR, fix rate y falsos positivos. "
            "Compara con la semana anterior e identifica mejoras "
            "y degradaciones. Sugiere ajustes de proceso. "
            "Máximo 500 palabras."
        ),
        "ciso": (
            "Genera un resumen ejecutivo de postura de seguridad "
            "para el CISO. Usa indicadores RAG (verde/ámbar/rojo) "
            "para cada métrica clave. Incluye riesgo residual y "
            "recomendaciones de inversión si procede. "
            "Máximo 200 palabras. Tono ejecutivo."
        ),
    }

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=(
            "Eres un analista de seguridad DevSecOps. Generas informes "
            "semanales a partir de métricas reales del pipeline. "
            "Sé preciso con los datos. No inventes números. "
            "Si una métrica empeoró, dilo con claridad. "
            "Usa español técnico."
        ),
        messages=[
            {
                "role": "user",
                "content": (
                    f"Métricas de la semana:\n"
                    f"{json.dumps(metrics, indent=2)}\n\n"
                    f"Cambios respecto a semana anterior:\n"
                    f"{json.dumps(deltas, indent=2)}\n\n"
                    f"{audience_prompts[audience]}"
                ),
            }
        ],
    )
    return message.content[0].text
