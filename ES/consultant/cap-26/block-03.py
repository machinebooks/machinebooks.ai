# Extraído de: LibroConsultor/cap-26-caso-seguridad.md
def generate_finding(
    control_id: str,
    document_evidence: list[dict],
    field_notes: list[str],
    cross_ref: ControlMapping
) -> dict:
    """Genera un hallazgo de auditoría completo para un control."""

    context = f"""Control: {control_id} - {cross_ref.iso_control}

    Evidencias documentales:
    {json.dumps(document_evidence, ensure_ascii=False, indent=2)}

    Notas de campo:
    {chr(10).join(f'- {note}' for note in field_notes)}

    Estado del cruce ISO/ENS:
    - Estado: {cross_ref.status}
    - Medidas ENS afectadas: {', '.join(cross_ref.ens_measures)}
    - Brecha preliminar: {cross_ref.gap_description}"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system="""Genera un hallazgo de auditoría profesional.
        Estructura: tipo (no conformidad mayor/menor/observación/
        oportunidad de mejora), descripción factual, evidencia,
        impacto en la organización, recomendación accionable,
        plazo de implementación sugerido.
        Tono: objetivo, preciso, sin juicios de valor.
        Idioma: español formal de auditoría.""",
        messages=[{"role": "user", "content": context}]
    )
    return parse_finding(response.content[0].text)
