# Extraído de: LibroConsultor/cap-27-caso-tecnologia.md
from claude_agent_sdk import Agent, tool

@tool
def evaluar_alternativa_tecnologica(
    alternativa: str,
    criterios: list[dict],
    contexto_cliente: dict
) -> dict:
    """Evalúa una alternativa tecnológica contra criterios ponderados del cliente.

    Args:
        alternativa: Nombre de la alternativa (ej: "microservicios con Spring Boot")
        criterios: Lista de criterios con nombre, peso y descripción
        contexto_cliente: Restricciones del cliente (cloud, equipo, regulación)
    """
    # El agente consulta su knowledge base de proyectos similares
    # y evalúa cada criterio con puntuación 1-5 y justificación
    ...

agent = Agent(
    model="claude-sonnet-4-6",
    tools=[evaluar_alternativa_tecnologica],
    system="""Eres un arquitecto de soluciones con experiencia en
modernización de sistemas legacy en el sector financiero/asegurador.
Evalúas alternativas tecnológicas con datos concretos, no opiniones.
Cuando no tengas datos suficientes, indica el nivel de incertidumbre."""
)
