# Extraído de: LibroCISO/cap-09-nis2-dora-tsunami.md
# Generación asistida del borrador de notificación NIS2
# El CISO revisa y modifica antes de enviar — nunca envío automático

import anthropic

client = anthropic.Anthropic()


def generate_nis2_notification_draft(
    incident: dict,
    phase: str,
    existing_notifications: list
) -> str:
    """Genera un borrador de notificación NIS2 para una fase.

    El borrador sigue la estructura exigida por el Art. 23 NIS2.
    El CISO SIEMPRE revisa y modifica antes de enviar.
    """
    phase_instructions = {
        "early_warning": (
            "Genera una alerta temprana concisa. Debe incluir: "
            "descripción breve del incidente, si se sospecha acto "
            "ilícito o malicioso, y si puede tener impacto transfronterizo. "
            "No requiere análisis profundo — es una primera comunicación."
        ),
        "formal": (
            "Genera una notificación formal que actualice la alerta "
            "temprana. Debe incluir: evaluación inicial de la gravedad "
            "e impacto, indicadores de compromiso conocidos, y primeras "
            "medidas de respuesta adoptadas."
        ),
        "final_report": (
            "Genera un informe final detallado. Debe incluir: "
            "descripción completa del incidente y su cronología, "
            "causa raíz probable, todas las medidas de mitigación "
            "adoptadas, impacto final cuantificado, y lecciones "
            "aprendidas."
        ),
    }

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=(
            "Eres un asistente especializado en ciberseguridad y "
            "cumplimiento normativo europeo. Generas borradores de "
            "notificaciones NIS2 (Directiva 2022/2555) que el CISO "
            "revisará antes de enviar a la autoridad competente. "
            "Usa lenguaje técnico preciso, sin adornos. Estructura "
            "la notificación con secciones claras."
        ),
        messages=[{
            "role": "user",
            "content": (
                f"Incidente: {incident['title']}\n"
                f"Descripción: {incident['description']}\n"
                f"Gravedad: {incident['severity']}\n"
                f"Detectado: {incident['detected_at']}\n"
                f"Servicios afectados: {incident['affected_services']}\n"
                f"¿Malicioso?: {incident['is_malicious']}\n"
                f"¿Transfronterizo?: {incident['is_cross_border']}\n\n"
                f"Fase: {phase}\n"
                f"Instrucciones: {phase_instructions[phase]}\n\n"
                f"Notificaciones previas: {existing_notifications}"
            )
        }]
    )

    return message.content[0].text
