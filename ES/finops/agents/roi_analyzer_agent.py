# Extraído de: LibroFinOps/cap-17-roi-humanbaseline.md
# agents/roi_analyzer_agent.py — Diagnóstico automático de caídas de ROI
import anthropic

client = anthropic.Anthropic()

def analyze_roi_anomaly(
    db, task_type: str, expected_roi: float,
    actual_roi: float, period_days: int = 7,
) -> str:
    """Usa Claude para analizar por qué el ROI cayó por debajo del umbral."""
    from services.roi_tracker import ROITracker
    tracker = ROITracker(db)
    summary = tracker.get_summary(days=period_days)
    task_data = summary.get("by_task_type", {}).get(task_type, {})

    prompt = f"""Analiza la caída de ROI en la tarea '{task_type}'.
ROI esperado: {expected_roi}:1 | ROI actual: {actual_roi}:1
Tareas completadas: {task_data.get('count', 0)}
Coste LLM: €{task_data.get('llm_cost', 0):.2f}
Valor liberado: €{task_data.get('value', 0):.2f}

Causas posibles: cambio en tasa de aceptación, aumento de overhead de supervisión,
cambio de modelo LLM por routing, cambio en mezcla de complejidad de clientes,
degradación de calidad del modelo.

Proporciona diagnóstico (máximo 200 palabras) con causas probables
y recomendación de acción para el equipo FinOps."""

    response = client.messages.create(
        model="claude-sonnet-4-6", max_tokens=400,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text
