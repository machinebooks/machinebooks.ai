# Extraído de: LibroConsultor/cap-11-inteligencia-competitiva.md
from claude_agent_sdk import Agent, tool
from dataclasses import dataclass

@dataclass
class InformeCompetitivo:
    """Informe periódico de inteligencia competitiva."""
    fecha: str
    resumen_ejecutivo: str
    movimientos_competidores: list[dict]
    tendencias_mercado: list[dict]
    oportunidades_detectadas: list[dict]
    alertas_pricing: list[dict]
    recomendaciones: list[dict]

@tool
def cruzar_fuentes_competitivas(
    adjudicaciones: list[dict],
    señales_empleo: dict,
    radar_tecnologico: dict,
    historial_propuestas: list[dict]
) -> InformeCompetitivo:
    """
    Cruza información de todas las fuentes para generar
    un informe competitivo integrado.

    Correlaciones que busca:
    - Competidor contrata perfiles X + aparece en adjudicaciones de Y
    - Tendencia tecnológica Z + cliente que licita en ese dominio
    - Precio de adjudicación vs nuestro precio histórico
    """
    # La lógica de cruce es el core del sistema:
    # 1. Mapa competidor → servicios → precios → tendencia
    # 2. Mapa cliente → historial → necesidades probables
    # 3. Mapa tendencia → oportunidad → competidores posicionados

    correlaciones = _ejecutar_correlaciones(
        adjudicaciones, señales_empleo,
        radar_tecnologico, historial_propuestas
    )

    return InformeCompetitivo(
        fecha=datetime.now().isoformat(),
        resumen_ejecutivo=correlaciones["resumen"],
        movimientos_competidores=correlaciones["competidores"],
        tendencias_mercado=correlaciones["tendencias"],
        oportunidades_detectadas=correlaciones["oportunidades"],
        alertas_pricing=correlaciones["pricing"],
        recomendaciones=correlaciones["recomendaciones"]
    )

@tool
def evaluar_posicion_competitiva(
    oportunidad: dict,
    competidores_probables: list[str],
    datos_historicos: dict
) -> dict:
    """
    Para una oportunidad concreta, evalúa nuestra posición
    competitiva frente a los competidores probables.
    """
    return {
        "oportunidad": oportunidad["titulo"],
        "competidores": [
            {
                "nombre": comp,
                "fortalezas": datos_historicos[comp]["fortalezas"],
                "precio_estimado": datos_historicos[comp]["precio_medio"],
                "historial_cliente": datos_historicos[comp].get(
                    "adjudicaciones_cliente", 0
                )
            }
            for comp in competidores_probables
        ],
        "nuestra_posicion": {
            "diferencial": _calcular_diferencial(oportunidad),
            "precio_recomendado": _recomendar_precio(
                oportunidad, datos_historicos
            ),
            "riesgo": _evaluar_riesgo_competitivo(
                competidores_probables, datos_historicos
            )
        }
    }

agente_mercado = Agent(
    model="claude-opus-4-6",
    tools=[cruzar_fuentes_competitivas, evaluar_posicion_competitiva],
    system="""Eres un analista de mercado senior para una consultora
    tecnológica. Tu trabajo es cruzar datos de múltiples fuentes
    públicas y generar inteligencia competitiva accionable.

    Principios:
    - Distingue hechos de inferencias. Marca cada conclusión con
      su nivel de confianza: alta (dato directo), media (inferencia
      con 2+ señales), baja (inferencia con 1 señal).
    - Las recomendaciones de pricing se basan en adjudicaciones
      públicas reales, no en suposiciones.
    - Nunca recomiendes precios predatorios. El objetivo es
      posicionamiento sostenible, no ganar a cualquier coste.
    - Señala siempre qué información falta para mejorar el análisis.
    """
)
