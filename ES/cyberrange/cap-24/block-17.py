# Extraído de: LibroCyberrange/cap-24-seguridad-plataforma.md
# Análisis de seguridad asistido por Claude
# Ejemplo didáctico: patrones/security/ai_audit_analysis.py

import anthropic

client = anthropic.Anthropic()

async def analyze_security_events(events: list[dict]) -> dict:
    """Analiza una serie de eventos de seguridad con Claude
    para detectar patrones complejos que las reglas estáticas no capturan.

    IMPORTANTE: Claude analiza y recomienda. No toma acciones automáticas.
    La decisión de bloquear, alertar o escalar es siempre humana."""

    events_summary = "\n".join([
        f"[{e['timestamp']}] {e['severity']}: {e['action']} "
        f"from {e['ip_address']} user={e['username']} "
        f"status={e['status']}"
        for e in events[:100]  # Limitar contexto a 100 eventos
    ])

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system="""Eres un analista de seguridad experto revisando logs
        de un Cyber Range. Identifica patrones sospechosos:
        - Actividad fuera de horario del ejercicio
        - Accesos entre workzones (debería estar aislado)
        - Intentos de acceso a recursos de administración
        - Patrones que sugieran herramientas automatizadas

        Responde en JSON con: findings (lista), risk_level (low/medium/high),
        recommended_actions (lista).""",
        messages=[{
            "role": "user",
            "content": f"Analiza estos eventos de las últimas 2 horas:\n\n{events_summary}"
        }]
    )

    return {
        "analysis": message.content[0].text,
        "events_analyzed": len(events),
        "model": "claude-sonnet-4-6",
        "disclaimer": "Análisis asistido por IA — requiere validación humana"
    }
