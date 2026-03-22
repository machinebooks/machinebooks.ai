# Extraído de: LibroDevSecOps/cap-26-caso-pipeline.md
def triage_findings(findings: list[dict], service_name: str) -> dict:
    """Envía hallazgos al agente de triaje y devuelve ranking priorizado."""
    findings_summary = json.dumps(findings[:50], indent=2)  # Lote de 50

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=(
            "Eres un agente de triaje de seguridad. Analiza cada hallazgo "
            "usando las tools disponibles para obtener contexto. Clasifica "
            "cada hallazgo en: INMEDIATO, PLANIFICADO, ACEPTAR_TEMPORAL, "
            "FALSO_POSITIVO. Justifica cada clasificación en una frase."
        ),
        tools=tools,
        messages=[{
            "role": "user",
            "content": f"Triaja estos hallazgos del servicio {service_name}:"
                       f"\n\n{findings_summary}"
        }]
    )
    # Procesar respuesta con tool_use loop (omitido por brevedad)
    return parse_triage_response(response)
