# Extraído de: LibroCISO/cap-14-gobernanza-ia-ai-act.md
# Ejemplo didáctico: agentes/ai_governance_agent.py
# Agente especializado en gobernanza de IA y conformidad AI Act

import anthropic

client = anthropic.Anthropic()


def evaluate_ai_system_conformity(
    system_description: str,
    risk_classification: dict,
    current_controls: list[dict],
    monitoring_metrics: list[dict]
) -> dict:
    """Usa Claude para evaluar la conformidad de un sistema de IA
    y generar recomendaciones específicas por checkpoint.

    Este agente NO decide la clasificación de riesgo (eso es determinista).
    SÍ evalúa si los controles existentes cubren los 7 requisitos
    y genera recomendaciones para cerrar gaps.
    """
    # Construir contexto con regulación relevante
    system_prompt = """Eres un agente especializado en conformidad con el AI Act europeo
    (Reglamento 2024/1689). Tu tarea es evaluar si los controles existentes de un sistema
    de IA cubren los 7 requisitos de conformidad (Art. 9-15) y generar recomendaciones
    específicas para cerrar gaps.

    Requisitos de conformidad:
    1. Art. 9 - Gestión de riesgos: sistema de gestión durante todo el ciclo de vida
    2. Art. 10 - Gobernanza de datos: calidad, representatividad, ausencia de sesgos
    3. Art. 11 - Documentación técnica: suficiente para demostrar conformidad
    4. Art. 12 - Registro de actividad: logging automático, trazabilidad
    5. Art. 13 - Transparencia: interpretabilidad, instrucciones de uso
    6. Art. 14 - Supervisión humana: HITL/HOTL/HIC según contexto
    7. Art. 15 - Precisión, robustez, ciberseguridad: niveles apropiados

    Evalúa cada requisito con: COVERED (controles suficientes), PARTIAL (controles
    insuficientes), GAP (sin controles), NOT_APPLICABLE (no aplica al sistema).

    Sé específico en las recomendaciones. No digas "mejorar la documentación" —
    di "añadir documentación sobre los datos de entrenamiento utilizados, incluyendo
    origen, fecha, volumen y proceso de limpieza".
    """

    user_message = f"""Evalúa la conformidad del siguiente sistema de IA:

SISTEMA: {system_description}

CLASIFICACIÓN DE RIESGO: {risk_classification}

CONTROLES EXISTENTES:
{_format_controls(current_controls)}

MÉTRICAS DE MONITORIZACIÓN:
{_format_metrics(monitoring_metrics)}

Para cada uno de los 7 requisitos (Art. 9-15), indica:
1. Estado: COVERED, PARTIAL, GAP o NOT_APPLICABLE
2. Controles que cubren el requisito (si los hay)
3. Gaps identificados
4. Recomendaciones específicas para cerrar gaps
5. Prioridad: HIGH, MEDIUM, LOW

Responde en formato JSON estructurado."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}]
    )

    return {
        "evaluation": message.content[0].text,
        "model_used": "claude-sonnet-4-6",
        "tokens_used": message.usage.input_tokens + message.usage.output_tokens,
        "requires_human_review": True  # Siempre. El agente sugiere; el humano decide.
    }


def _format_controls(controls: list[dict]) -> str:
    """Formatea controles para el prompt del agente."""
    if not controls:
        return "No hay controles registrados."
    return "\n".join(
        f"- [{c.get('ai_act_article', 'N/A')}] {c['control_name']}: "
        f"{c['control_description']} (Estado: {c.get('implementation_status', 'desconocido')})"
        for c in controls
    )


def _format_metrics(metrics: list[dict]) -> str:
    """Formatea métricas para el prompt del agente."""
    if not metrics:
        return "No hay métricas de monitorización registradas."
    return "\n".join(
        f"- {m['metric_type']}: valor={m['value']}, "
        f"alerta={m.get('alert_level', 'N/A')}, "
        f"tendencia={m.get('trend', 'N/A')}"
        for m in metrics
    )
