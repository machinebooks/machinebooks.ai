# Extraído de: LibroConsultor/cap-29-futuro-consultor.md
from claude_agent_sdk import Agent, tool
import anthropic
from datetime import datetime

@tool
def evaluar_postura_seguridad(cliente_id: str) -> dict:
    """Evalúa la postura de seguridad actual del cliente
    contra el framework de referencia pactado."""
    # Obtiene evidencias actualizadas via MCP
    evidencias = obtener_evidencias_cliente(cliente_id)
    controles = obtener_framework_cliente(cliente_id)

    client = anthropic.Anthropic()
    evaluacion = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system="""Eres un auditor de seguridad. Evalúa cada control
        contra las evidencias proporcionadas. Clasifica:
        cumple / cumple_parcial / no_cumple / sin_evidencia.
        Para no_cumple, indica riesgo (alto/medio/bajo) y
        acción correctiva concreta con plazo estimado.""",
        messages=[{
            "role": "user",
            "content": f"Controles: {controles}\nEvidencias: {evidencias}"
        }]
    )
    return {"evaluacion": evaluacion.content, "fecha": datetime.now().isoformat()}

@tool
def generar_alerta_si_necesaria(evaluacion: dict,
                                 umbral_riesgo: str = "alto") -> dict:
    """Genera alerta solo si hay controles no cumplidos
    con riesgo igual o superior al umbral."""
    # Filtra hallazgos por umbral de riesgo
    # Genera alerta con contexto y recomendación
    # Envía al consultor senior si requiere intervención humana
    ...
