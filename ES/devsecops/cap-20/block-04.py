# Extraído de: LibroDevSecOps/cap-20-respuesta-incidentes.md
def generate_postmortem_draft(incident_id: str) -> str:
    """Genera un borrador de post-mortem usando Claude."""

    # Recopilar todos los datos del incidente
    incident_data = get_incident_data(incident_id)
    actions = [a for a in action_log if a["incident_id"] == incident_id]

    prompt = f"""Genera un post-mortem estructurado para el siguiente incidente.
Usa el formato blameless (sin culpas, enfocado en sistemas y procesos).

## Datos del incidente
- ID: {incident_data['incident_id']}
- Severidad: {incident_data['severity']}
- Detectado: {incident_data['detected_at']}
- Contenido: {incident_data['contained_at']}
- Resuelto: {incident_data['resolved_at']}

## Alertas correladas
{json.dumps(incident_data['alerts'], indent=2, default=str)}

## Acciones ejecutadas
{json.dumps(actions, indent=2, default=str)}

## Servicios afectados
{json.dumps(incident_data['affected_services'], indent=2)}

## Estructura requerida
1. Resumen ejecutivo (3-5 frases)
2. Timeline detallado con timestamps
3. Causa raíz (5 Whys)
4. Impacto (usuarios afectados, duración, datos comprometidos)
5. Qué funcionó bien
6. Qué se puede mejorar
7. Action items con owner y fecha límite
8. Métricas: MTTD, MTTC, MTTR

IMPORTANTE: No inventes datos. Si alguna información no está disponible
en los datos proporcionados, indica explícitamente "[PENDIENTE: completar
con equipo de guardia]"."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text
