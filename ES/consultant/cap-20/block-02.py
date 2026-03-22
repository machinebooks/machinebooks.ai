# Extraído de: LibroConsultor/cap-20-pricing.md
import anthropic
from typing import Optional

client = anthropic.Anthropic()

SYSTEM_PROMPT = """Eres un analista financiero especializado en consultoría tecnológica.
Recibes un pipeline de proyectos con pricing calculado y debes:
1. Proyectar facturación anual bajo cada modelo de pricing.
2. Calcular margen bruto y neto (asumiendo 22% de costes fijos generales).
3. Identificar la combinación óptima de modelos por tipo de proyecto.
4. Señalar riesgos: concentración de ingresos, dependencia de variable, etc.
Responde en JSON estructurado con campos: facturacion_total, margen_bruto,
margen_neto, mix_recomendado, riesgos, y narrativa (texto explicativo de 3-5 frases)."""

def simular_pipeline_anual(
    proyectos: list[dict],
    modelo_pricing: str = "hybrid"
) -> dict:
    """Simula la rentabilidad anual de un pipeline de proyectos."""
    # Preparar resumen del pipeline para el agente
    resumen = []
    for p in proyectos:
        pricing = calcular_pricing(ProyectoInput(**p))
        resumen.append({
            "tipo": p["tipo"],
            "sector": p["sector"],
            "precio_recomendado": getattr(pricing, f"precio_{pricing.modelo_recomendado}"),
            "margen_recomendado": getattr(pricing, f"margen_{pricing.modelo_recomendado}"),
            "modelo": pricing.modelo_recomendado,
            "horas_equipo": p["horas_estimadas_sin_ia"] * p["factor_reduccion_ia"],
        })

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"Pipeline de proyectos para el año:\n{resumen}\n\n"
                       f"Modelo base solicitado: {modelo_pricing}\n"
                       f"Calcula proyección anual y mix óptimo."
        }]
    )
    return message.content[0].text
