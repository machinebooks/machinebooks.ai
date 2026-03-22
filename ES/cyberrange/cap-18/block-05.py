# Extraído de: LibroCyberrange/cap-18-coaching-ia.md
# Ejemplo didáctico: cyber-range-builder/backend/services/ai/evaluation_prompts.py

def get_evaluation_system_prompt() -> str:
    return """Eres un evaluador experto de ciberseguridad que analiza sesiones
de entrenamiento en un Cyber Range profesional. Tu objetivo es generar
un informe de aprendizaje constructivo y accionable.

FORMATO DEL INFORME (JSON):
{
    "summary": "Resumen ejecutivo de 2-3 frases",
    "completion_assessment": "completed|partial|abandoned",
    "time_efficiency": "Análisis del uso del tiempo",
    "strengths": [
        {"skill": "nombre", "evidence": "qué hizo bien", "mitre": "T1234"}
    ],
    "gaps": [
        {"skill": "nombre", "description": "qué le faltó", "mitre": "T1234"}
    ],
    "stall_analysis": [
        {"moment": "HH:MM", "duration_min": N, "cause": "análisis",
         "what_would_have_helped": "conocimiento o técnica"}
    ],
    "kill_chain_coverage": {
        "recon": {"covered": true/false, "depth": "basic|intermediate|thorough"},
        "initial_access": {...},
        "privilege_escalation": {...},
        "lateral_movement": {...},
        "exfiltration": {...}
    },
    "recommended_exercises": [
        {"title": "nombre sugerido", "focus": "qué entrena",
         "difficulty": "beginner|intermediate|advanced",
         "mitre_techniques": ["T1234"]}
    ],
    "overall_score": {
        "technical": 1-10,
        "methodology": 1-10,
        "efficiency": 1-10,
        "comments": "justificación"
    }
}

REGLAS:
- Sé constructivo: incluso en sesiones pobres, identifica algo positivo.
- Sé específico: referencia comandos concretos como evidencia.
- Las recomendaciones deben ser accionables y mapeadas a MITRE ATT&CK.
- No inventes técnicas MITRE: usa solo IDs reales (T1xxx, T1xxx.xxx)."""


def build_evaluation_prompt(
    context: "PlayerContext",
    full_actions: list
) -> str:
    """
    Construye el prompt para análisis post-ejercicio completo.
    Incluye TODAS las acciones del jugador (no solo las recientes).
    """
    # Agrupar acciones por fase temporal
    phases = []
    current_phase_start = None
    current_category = None

    for action in full_actions:
        if action.category != current_category:
            if current_phase_start:
                phases.append({
                    "start": current_phase_start.strftime('%H:%M'),
                    "end": action.timestamp.strftime('%H:%M'),
                    "category": current_category,
                    "commands": phase_commands
                })
            current_phase_start = action.timestamp
            current_category = action.category
            phase_commands = []
        phase_commands.append(action.command)

    # Última fase
    if current_phase_start and full_actions:
        phases.append({
            "start": current_phase_start.strftime('%H:%M'),
            "end": full_actions[-1].timestamp.strftime('%H:%M'),
            "category": current_category,
            "commands": phase_commands
        })

    phases_text = ""
    for i, phase in enumerate(phases, 1):
        cmds = "\n    ".join(phase["commands"][:20])  # Limitar para no exceder contexto
        phases_text += f"""
  Fase {i} ({phase['start']}-{phase['end']}): {phase['category']}
    {cmds}
"""

    hints_text = "\n".join([
        f"  - Nivel {h['level']}: {h['text']}"
        for h in context.hints_given
    ]) or "  No usó pistas."

    return f"""RETO COMPLETADO:
- Título: {context.challenge_title}
- Dificultad: {context.difficulty}
- Técnicas MITRE: {', '.join(context.mitre_techniques)}
- Ruta esperada: {context.solution_path}
- Tiempo total: {context.time_elapsed_minutes} minutos
- Intentos de flag fallidos: {context.flag_attempts_failed}

ACCIONES DEL JUGADOR (organizadas por fases):
{phases_text}

PISTAS UTILIZADAS:
{hints_text}

Genera el informe de evaluación en formato JSON."""
