# Extraído de: LibroConsultor/cap-22-unit-economics.md
import anthropic

def generate_quarterly_analysis(tracker: ROITracker, quarter: str) -> str:
    """Genera análisis narrativo del ROI trimestral con Claude."""
    client = anthropic.Anthropic()

    # Preparar datos para el contexto
    summary = {
        "quarter": quarter,
        "total_projects": len(tracker.records),
        "total_hours_saved": tracker.total_hours_saved,
        "aggregate_roi": f"{tracker.aggregate_roi:.1f}x",
        "avg_compression": f"{tracker.avg_compression:.0%}",
        "by_type": tracker.by_project_type(),
        "total_ai_investment": tracker.total_ai_cost,
        "total_incremental_margin": tracker.total_incremental_margin,
    }

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system="""Eres un analista financiero de una práctica de consultoría
tecnológica. Analiza los datos de ROI de herramientas de IA y genera un
informe ejecutivo en español. Incluye: resumen de rendimiento, tendencias
por tipo de proyecto, alertas si algún tipo tiene ROI inferior a 5x,
y recomendaciones para el próximo trimestre. Sé directo, usa datos.""",
        messages=[{
            "role": "user",
            "content": (
                f"Datos del trimestre {quarter}:\n"
                f"{json.dumps(summary, indent=2, ensure_ascii=False)}"
            )
        }]
    )
    return message.content[0].text
