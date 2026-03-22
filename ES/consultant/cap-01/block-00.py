# Extraído de: LibroConsultor/cap-01-crisis-consultoria.md
import anthropic
from dataclasses import dataclass

@dataclass
class RFPAnalysis:
    """Resultado estructurado del análisis de un RFP."""
    requisitos_obligatorios: list[dict]   # Requisitos de solvencia y capacidad
    criterios_valoracion: list[dict]      # Criterios con ponderación
    plazos: dict                          # Fechas clave del proceso
    perfiles_exigidos: list[dict]         # Perfiles profesionales requeridos
    penalizaciones: list[str]             # Cláusulas de penalización
    presupuesto_maximo: float | None      # Presupuesto base si se indica
    recomendacion_go_nogo: str            # "GO", "NO-GO" o "EVALUAR"
    justificacion: str                    # Razón de la recomendación

client = anthropic.Anthropic(api_key="<TU_ANTHROPIC_KEY>")

def analyze_rfp(document_text: str, practice_context: str) -> RFPAnalysis:
    """Analiza un RFP y extrae elementos clave para decisión go/no-go."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8192,
        system="""Eres un analista senior de consultoría tecnológica
especializado en licitaciones del sector público español.
Analiza el documento de requisitos y extrae la información
estructurada que un equipo de preventa necesita para decidir
si presentar oferta y, en caso afirmativo, preparar la propuesta.

Sé exhaustivo con los requisitos obligatorios — omitir uno
significa descalificación. Sé preciso con las ponderaciones
de los criterios de valoración. Indica explícitamente si
algún dato no aparece en el documento.""",
        messages=[{
            "role": "user",
            "content": f"""Analiza este RFP:

--- DOCUMENTO ---
{document_text}
--- FIN DOCUMENTO ---

--- CONTEXTO DE LA PRÁCTICA ---
{practice_context}
--- FIN CONTEXTO ---

Devuelve el análisis en formato JSON estructurado."""
        }]
    )
    # Parsear respuesta JSON a RFPAnalysis
    return parse_analysis(message.content[0].text)
