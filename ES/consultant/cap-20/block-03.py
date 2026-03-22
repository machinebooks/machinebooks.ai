# Extraído de: LibroConsultor/cap-20-pricing.md
from claude_agent_sdk import Agent, tool
import json

@tool
def calcular_precio_proyecto(
    tipo: str,
    sector: str,
    alcance: str,
    frameworks: str,
    horas_estimadas: int,
    valor_cliente: float,
    es_licitacion: bool = False,
    cliente_recurrente: bool = False
) -> str:
    """Calcula el pricing recomendado para un proyecto de consultoría.

    Args:
        tipo: Tipo de proyecto (auditoria, gap_analysis, roadmap, assessment)
        sector: Sector del cliente (financiero, publico, energia, salud)
        alcance: Descripción del alcance
        frameworks: Frameworks separados por coma (ISO27001,ENS,NIS2)
        horas_estimadas: Horas estimadas sin IA
        valor_cliente: Valor estimado del resultado para el cliente
        es_licitacion: Si es licitación pública
        cliente_recurrente: Si es cliente existente
    """
    # Factor de reducción por tipo de proyecto
    factores = {
        "auditoria": 0.40, "gap_analysis": 0.45,
        "roadmap": 0.75, "assessment": 0.55
    }

    proyecto = ProyectoInput(
        tipo=tipo, sector=sector, alcance=alcance,
        frameworks=frameworks.split(","),
        horas_estimadas_sin_ia=horas_estimadas,
        factor_reduccion_ia=factores.get(tipo, 0.50),
        valor_cliente_estimado=valor_cliente,
        es_licitacion_publica=es_licitacion,
        cliente_recurrente=cliente_recurrente
    )
    resultado = calcular_pricing(proyecto)
    return json.dumps({
        "recomendacion": resultado.modelo_recomendado,
        "precios": {
            "cost_plus": f"€{resultado.precio_cost_plus:,.0f}",
            "value_based": f"€{resultado.precio_value_based:,.0f}",
            "hybrid": f"€{resultado.precio_hybrid:,.0f}",
            "retainer_mensual": f"€{resultado.precio_retainer_mensual:,.0f}",
        },
        "margenes": {
            "cost_plus": f"{resultado.margen_cost_plus:.1%}",
            "value_based": f"{resultado.margen_value_based:.1%}",
            "hybrid": f"{resultado.margen_hybrid:.1%}",
        },
        "justificacion": resultado.justificacion,
        "riesgos": resultado.riesgos,
    }, indent=2, ensure_ascii=False)

@tool
def comparar_con_historico(tipo: str, sector: str, precio_propuesto: float) -> str:
    """Compara un precio propuesto contra el histórico de proyectos similares.

    Busca proyectos del mismo tipo y sector para calibrar si el precio
    está en rango, por debajo del mercado o por encima.
    """
    # Simulación de consulta a BD histórica (datos escalados)
    historico = {
        ("auditoria", "publico"): {"media": 52000, "min": 35000, "max": 78000, "n": 14},
        ("auditoria", "financiero"): {"media": 68000, "min": 45000, "max": 95000, "n": 8},
        ("gap_analysis", "publico"): {"media": 38000, "min": 22000, "max": 58000, "n": 11},
        ("gap_analysis", "energia"): {"media": 45000, "min": 30000, "max": 72000, "n": 6},
        ("assessment", "publico"): {"media": 28000, "min": 18000, "max": 42000, "n": 9},
        ("roadmap", "financiero"): {"media": 55000, "min": 35000, "max": 85000, "n": 5},
    }

    datos = historico.get((tipo, sector))
    if not datos:
        return json.dumps({"error": "Sin datos históricos para esta combinación"})

    percentil = (precio_propuesto - datos["min"]) / (datos["max"] - datos["min"])
    posicion = "bajo" if percentil < 0.3 else "medio" if percentil < 0.7 else "alto"

    return json.dumps({
        "precio_propuesto": f"€{precio_propuesto:,.0f}",
        "media_historica": f"€{datos['media']:,.0f}",
        "rango": f"€{datos['min']:,.0f} - €{datos['max']:,.0f}",
        "posicion": posicion,
        "percentil": f"{percentil:.0%}",
        "proyectos_comparados": datos["n"],
    }, indent=2, ensure_ascii=False)

# Configuración del agente
pricing_agent = Agent(
    model="claude-sonnet-4-6",
    tools=[calcular_precio_proyecto, comparar_con_historico],
    system="""Eres el agente de pricing de una práctica de consultoría tecnológica.
Tu rol: ayudar al equipo comercial a fijar precios que maximicen el margen
sin perder competitividad. Siempre explica el razonamiento detrás de tu
recomendación y alerta sobre riesgos comerciales."""
)
