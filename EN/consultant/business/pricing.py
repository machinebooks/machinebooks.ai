# Source: The Consultant and the Machine -- Chapter 20
# Pattern: AI-assisted pricing: models, simulation, blind spots
import anthropic
from dataclasses import dataclass, field

@dataclass
class ProyectoInput:
    """Input parameters for pricing calculation."""
    tipo: str                    # "auditoria", "gap_analysis", "roadmap", "assessment"
    sector: str                  # "financiero", "publico", "energia", "salud"
    alcance: str                 # Free-text scope description
    frameworks: list[str]        # ["ISO27001", "ENS", "NIS2", "DORA"]
    horas_estimadas_sin_ia: int  # Traditional estimate
    factor_reduccion_ia: float   # 0.4 = 60% reduction
    valor_cliente_estimado: float  # Estimated result value for the client
    es_licitacion_publica: bool
    cliente_recurrente: bool
    num_retainers_activos: int = 0  # For subscription viability calculation

@dataclass
class PricingResult:
    """Pricing calculation result."""
    modelo_recomendado: str
    precio_cost_plus: float
    precio_value_based: float
    precio_hybrid: float
    precio_retainer_mensual: float
    margen_cost_plus: float
    margen_value_based: float
    margen_hybrid: float
    margen_retainer: float
    justificacion: str
    riesgos: list[str] = field(default_factory=list)

# --- Block 2 ---

# Base rates and costs (scaled, not real values)
COSTE_HORA_CARGADO = 175.0      # Company cost per consultant hour
COSTE_IA_POR_HORA = 3.50        # Tokens + infra per AI-assisted project hour
MARGEN_OBJETIVO_COST_PLUS = 0.38
PORCENTAJE_VALOR_CLIENTE = 0.12  # 12% of identified value
FEE_FIJO_RATIO = 0.75           # Fixed proportion of hybrid
BONUS_RATIO = 0.08              # 8% of demonstrable savings

def calcular_pricing(proyecto: ProyectoInput) -> PricingResult:
    """Calculates pricing under all four models."""
    horas_con_ia = proyecto.horas_estimadas_sin_ia * proyecto.factor_reduccion_ia
    coste_equipo = horas_con_ia * COSTE_HORA_CARGADO
    coste_ia = horas_con_ia * COSTE_IA_POR_HORA
    coste_base = coste_equipo + coste_ia

    # Model 1: Cost-plus
    precio_cp = coste_base * (1 + MARGEN_OBJETIVO_COST_PLUS)
    margen_cp = (precio_cp - coste_base) / precio_cp

    # Model 2: Value-based
    precio_vb = proyecto.valor_cliente_estimado * PORCENTAJE_VALOR_CLIENTE
    precio_vb = max(precio_vb, coste_base * 1.15)  # Floor: cost + 15%
    margen_vb = (precio_vb - coste_base) / precio_vb

    # Model 3: Hybrid (fixed fee + variable)
    fee_fijo = precio_cp * 1.15 * FEE_FIJO_RATIO  # Base 15% over cost-plus
    bonus_estimado = proyecto.valor_cliente_estimado * BONUS_RATIO * 0.6
    precio_hy = fee_fijo + bonus_estimado  # Conservative estimate
    margen_hy = (precio_hy - coste_base) / precio_hy

    # Model 4: Monthly retainer (if applicable)
    precio_ret = (coste_base / 6) * 1.55 if proyecto.cliente_recurrente else 0
    margen_ret = 0.55 if proyecto.cliente_recurrente else 0

    # Recommendation logic
    if proyecto.es_licitacion_publica:
        recomendado = "cost_plus"
        justificacion = "Public tender: rigid bid structure required"
    elif proyecto.cliente_recurrente and proyecto.num_retainers_activos >= 10:
        recomendado = "retainer"
        justificacion = "Recurring client with critical retainer mass"
    elif proyecto.valor_cliente_estimado > coste_base * 5:
        recomendado = "hybrid"
        justificacion = "High client value, hybrid captures upside"
    else:
        recomendado = "cost_plus"
        justificacion = "Standard value/cost ratio, cost-plus is safer"

    return PricingResult(
        modelo_recomendado=recomendado,
        precio_cost_plus=round(precio_cp, 2),
        precio_value_based=round(precio_vb, 2),
        precio_hybrid=round(precio_hy, 2),
        precio_retainer_mensual=round(precio_ret, 2),
        margen_cost_plus=round(margen_cp, 4),
        margen_value_based=round(margen_vb, 4),
        margen_hybrid=round(margen_hy, 4),
        margen_retainer=round(margen_ret, 4),
        justificacion=justificacion,
        riesgos=_identificar_riesgos(proyecto, coste_base)
    )

# --- Block 3 ---

import anthropic
from typing import Optional

client = anthropic.Anthropic(api_key="<YOUR_API_KEY>")

SYSTEM_PROMPT = """You are a financial analyst specialized in technology consulting.
You receive a project pipeline with calculated pricing and must:
1. Project annual revenue under each pricing model.
2. Calculate gross and net margin (assuming 22% general fixed costs).
3. Identify the optimal model combination by project type.
4. Flag risks: revenue concentration, variable dependency, etc.
Respond in structured JSON with fields: facturacion_total, margen_bruto,
margen_neto, mix_recomendado, riesgos, and narrativa (3-5 sentence explanatory text)."""

def simular_pipeline_anual(
    proyectos: list[dict],
    modelo_pricing: str = "hybrid"
) -> dict:
    """Simulates annual profitability of a project pipeline."""
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
            "content": f"Project pipeline for the year:\n{resumen}\n\n"
                       f"Requested base model: {modelo_pricing}\n"
                       f"Calculate annual projection and optimal mix."
        }]
    )
    return message.content[0].text

# --- Block 4 ---

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
    """Calculates recommended pricing for a consulting project.

    Args:
        tipo: Project type (auditoria, gap_analysis, roadmap, assessment)
        sector: Client sector (financiero, publico, energia, salud)
        alcance: Scope description
        frameworks: Comma-separated frameworks (ISO27001,ENS,NIS2)
        horas_estimadas: Estimated hours without AI
        valor_cliente: Estimated result value for the client
        es_licitacion: Whether it's a public tender
        cliente_recurrente: Whether it's an existing client
    """
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
    """Compares a proposed price against the historical record of similar projects.

    Searches projects of the same type and sector to calibrate whether
    the price is in range, below market, or above.
    """
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
        return json.dumps({"error": "No historical data for this combination"})

    percentil = (precio_propuesto - datos["min"]) / (datos["max"] - datos["min"])
    posicion = "low" if percentil < 0.3 else "mid" if percentil < 0.7 else "high"

    return json.dumps({
        "precio_propuesto": f"€{precio_propuesto:,.0f}",
        "media_historica": f"€{datos['media']:,.0f}",
        "rango": f"€{datos['min']:,.0f} - €{datos['max']:,.0f}",
        "posicion": posicion,
        "percentil": f"{percentil:.0%}",
        "proyectos_comparados": datos["n"],
    }, indent=2, ensure_ascii=False)

# Agent configuration
pricing_agent = Agent(
    model="claude-sonnet-4-6",
    tools=[calcular_precio_proyecto, comparar_con_historico],
    system="""You are the pricing agent of a technology consulting practice.
Your role: help the commercial team set prices that maximize margin
without losing competitiveness. Always explain the reasoning behind
your recommendation and alert about commercial risks."""
)

# --- Block 5 ---

def _identificar_riesgos(
    proyecto: ProyectoInput, coste_base: float
) -> list[str]:
    """Identifies commercial risks of the proposed pricing."""
    riesgos = []

    if proyecto.horas_estimadas_sin_ia < 100:
        riesgos.append(
            "Small project: management fixed costs may erode margin"
        )

    if not proyecto.es_licitacion_publica and proyecto.tipo in ("roadmap", "assessment"):
        riesgos.append(
            "High scope creep risk on fixed fee — define deliverables precisely"
        )

    if proyecto.valor_cliente_estimado > coste_base * 8:
        riesgos.append(
            "Variable component depends on client implementing recommendations"
        )

    if proyecto.sector == "publico" and not proyecto.es_licitacion_publica:
        riesgos.append(
            "Public sector price-sensitive — prepare value argumentation"
        )

    if proyecto.factor_reduccion_ia < 0.5:
        riesgos.append(
            ">50% AI reduction visible — prepare value narrative, not savings narrative"
        )

    return riesgos

# --- Block 6 ---

@tool
def calcular_breakeven_retainer(
    coste_mensual_automatizacion: float,
    coste_mensual_equipo_dedicado: float,
    precio_retainer_mensual: float,
    horas_consultor_incluidas: int
) -> str:
    """Calculates break-even for a retainer model.

    Args:
        coste_mensual_automatizacion: Monthly AI infrastructure cost
        coste_mensual_equipo_dedicado: Dedicated team cost (partial)
        precio_retainer_mensual: Client retainer price
        horas_consultor_incluidas: Senior consultant hours included/month
    """
    coste_hora_senior = 195.0  # Loaded cost
    coste_horas = horas_consultor_incluidas * coste_hora_senior
    coste_total_mensual = (
        coste_mensual_automatizacion + coste_mensual_equipo_dedicado + coste_horas
    )
    margen_por_cliente = precio_retainer_mensual - coste_total_mensual

    costes_fijos_mensuales = 4200  # Platform, monitoring, maintenance

    if margen_por_cliente <= 0:
        return json.dumps({
            "viable": False,
            "mensaje": "Retainer does not cover per-client variable costs"
        })

    clientes_breakeven = costes_fijos_mensuales / margen_por_cliente

    return json.dumps({
        "viable": True,
        "coste_por_cliente_mes": f"€{coste_total_mensual:,.0f}",
        "margen_por_cliente_mes": f"€{margen_por_cliente:,.0f}",
        "clientes_breakeven": round(clientes_breakeven, 1),
        "margen_con_15_clientes": f"€{(margen_por_cliente * 15 - costes_fijos_mensuales):,.0f}/mes",
        "arr_con_15_clientes": f"€{precio_retainer_mensual * 15 * 12:,.0f}",
    }, indent=2, ensure_ascii=False)
