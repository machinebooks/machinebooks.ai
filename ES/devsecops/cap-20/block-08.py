# Extraído de: LibroDevSecOps/cap-20-respuesta-incidentes.md
def generate_incident_communications(
    incident: CorrelatedIncident,
    audiences: list[str]
) -> dict[str, str]:
    """Genera borradores de comunicación adaptados por audiencia."""
    communications = {}

    audience_prompts = {
        "executive": (
            "Genera un resumen ejecutivo de 5-7 líneas para dirección. "
            "Sin jerga técnica. Incluye: qué ocurrió (1 frase), "
            "impacto en el servicio, estado actual de la contención "
            "y próximos pasos. Tono: informativo, sin alarma innecesaria."
        ),
        "engineering": (
            "Genera un resumen técnico para el equipo de desarrollo. "
            "Incluye: vector de ataque, servicios afectados, CVEs "
            "involucradas, acciones de contención ejecutadas y PRs "
            "de remediación pendientes. Incluye comandos útiles para "
            "verificar el estado de los servicios afectados."
        ),
        "regulatory": (
            "Genera un borrador de notificación para la autoridad "
            "de protección de datos según el artículo 33 del RGPD. "
            "Incluye: naturaleza de la brecha, categorías de datos "
            "afectados, número aproximado de registros, medidas "
            "adoptadas y punto de contacto del DPO. Marca con "
            "[PENDIENTE] toda información que requiera verificación."
        )
    }

    for audience in audiences:
        if audience not in audience_prompts:
            continue
        context = format_incident_for_communication(incident)
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[{"role": "user", "content": (
                f"{audience_prompts[audience]}\n\n"
                f"Datos del incidente:\n{context}"
            )}]
        )
        communications[audience] = response.content[0].text

    return communications
