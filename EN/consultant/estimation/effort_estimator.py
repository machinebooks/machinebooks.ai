# Source: The Consultant and the Machine -- Chapter 10
# Pattern: AI-calibrated estimation with historical data
from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional

class TipoServicio(str, Enum):
    AUDITORIA = "auditoria"
    GAP_ANALYSIS = "gap_analysis"
    ARQUITECTURA = "arquitectura"
    IMPLANTACION = "implantacion"
    CONSULTORIA_ESTRATEGICA = "consultoria_estrategica"
    ASSESSMENT = "assessment"

class ComplejidadRegulatoria(str, Enum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"

class ProyectoHistorico(BaseModel):
    """Record of a completed project with actual data."""
    id: str
    nombre: str  # anonymized: "ENS audit public sector 2024"
    descripcion_alcance: str  # free text for semantic search
    tipo_servicio: TipoServicio
    sector: str
    complejidad_regulatoria: ComplejidadRegulatoria
    tecnologias: list[str]
    # Original estimate
    horas_estimadas: float
    duracion_semanas_estimada: int
    equipo_estimado: int  # number of consultants
    # Actual result
    horas_reales: float
    duracion_semanas_real: int
    equipo_real: int
    # Derived metrics
    ratio_desviacion: float = Field(
        default=0.0,
        description="horas_reales / horas_estimadas"
    )
    factores_desviacion: Optional[str] = None  # what caused the deviation
    fecha_cierre: str  # YYYY-MM format

# --- Block 2 ---

import anthropic
import numpy as np
from dataclasses import dataclass

@dataclass
class SimilitudProyecto:
    proyecto: ProyectoHistorico
    score_semantico: float  # 0-1, embedding similarity
    score_estructural: float  # 0-1, attribute match
    score_combinado: float  # weighted combination

def calcular_similitud_estructural(
    nuevo: dict, historico: ProyectoHistorico
) -> float:
    """Compares discrete attributes between new and historical project."""
    score = 0.0
    pesos = {
        "tipo_servicio": 0.30,
        "sector": 0.25,
        "complejidad_regulatoria": 0.20,
        "tecnologias": 0.25,
    }
    # Service type: exact match
    if nuevo["tipo_servicio"] == historico.tipo_servicio.value:
        score += pesos["tipo_servicio"]
    # Sector: exact match
    if nuevo["sector"] == historico.sector:
        score += pesos["sector"]
    # Regulatory complexity: penalize difference
    niveles = {"baja": 1, "media": 2, "alta": 3}
    diff = abs(
        niveles[nuevo["complejidad_regulatoria"]]
        - niveles[historico.complejidad_regulatoria.value]
    )
    score += pesos["complejidad_regulatoria"] * max(0, 1 - diff * 0.5)
    # Technologies: Jaccard similarity
    set_nuevo = set(nuevo.get("tecnologias", []))
    set_hist = set(historico.tecnologias)
    if set_nuevo | set_hist:
        jaccard = len(set_nuevo & set_hist) / len(set_nuevo | set_hist)
        score += pesos["tecnologias"] * jaccard
    return score

# --- Block 3 ---

import anthropic
import json

client = anthropic.Anthropic(api_key="<YOUR_API_KEY>")

# Tools the agent can invoke
tools = [
    {
        "name": "buscar_proyectos_similares",
        "description": (
            "Searches for historical projects similar to the described project. "
            "Returns the N most similar with their similarity score."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "descripcion_alcance": {
                    "type": "string",
                    "description": "Scope description of the new project"
                },
                "tipo_servicio": {"type": "string"},
                "sector": {"type": "string"},
                "complejidad_regulatoria": {"type": "string"},
                "tecnologias": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "top_n": {
                    "type": "integer",
                    "description": "Number of similar projects to return"
                }
            },
            "required": [
                "descripcion_alcance", "tipo_servicio", "sector"
            ]
        }
    },
    {
        "name": "calcular_estimacion_calibrada",
        "description": (
            "Calculates calibrated effort estimation from "
            "similar projects and their historical deviations."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "ids_proyectos_referencia": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "horas_estimadas_base": {
                    "type": "number",
                    "description": "Consultant's base estimate (hours)"
                },
                "nivel_confianza": {
                    "type": "number",
                    "description": "Desired confidence level (0.80, 0.90)"
                }
            },
            "required": [
                "ids_proyectos_referencia", "horas_estimadas_base"
            ]
        }
    }
]

SYSTEM_PROMPT = """You are an effort estimation agent for technology
consulting projects. Your task:

1. Receive the description of a new project.
2. Search for similar historical projects in the database.
3. Analyze the historical deviations of those projects.
4. Produce a calibrated estimate with confidence interval.

Rules:
- Always search for at least 5 similar projects.
- If you find fewer than 3 with similarity > 0.6, mark as "low confidence."
- Explain which projects you used as reference and why.
- Include the average deviation ratio of the reference projects.
- Produce a range (P10-P90), not a single number.
- Identify specific risk factors of the new project
  that could increase deviation."""

def ejecutar_estimacion(descripcion_proyecto: str) -> dict:
    """Runs the estimation agent on a new project."""
    messages = [
        {"role": "user", "content": descripcion_proyecto}
    ]
    # Agent loop: the model iteratively invokes tools
    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=tools,
            messages=messages
        )
        # If the model finishes without invoking tools, return
        if response.stop_reason == "end_turn":
            return {
                "estimacion": response.content[0].text,
                "tokens_usados": response.usage.input_tokens
                    + response.usage.output_tokens
            }
        # Process tool invocations
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                resultado = ejecutar_herramienta(
                    block.name, block.input
                )
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(resultado)
                })
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})

# --- Block 4 ---

from dataclasses import dataclass
import statistics

@dataclass
class EstimacionCalibrada:
    horas_base: float            # consultant's estimate
    horas_calibrada: float       # adjusted for historical bias
    intervalo_p10: float         # 10th percentile (optimistic)
    intervalo_p50: float         # 50th percentile (most likely)
    intervalo_p90: float         # 90th percentile (pessimistic)
    confianza: str               # "high", "medium", "low"
    n_proyectos_referencia: int
    ratio_desviacion_medio: float
    factores_riesgo: list[str]

def calibrar_estimacion(
    horas_base: float,
    proyectos_referencia: list[ProyectoHistorico],
    nivel_confianza: float = 0.80
) -> EstimacionCalibrada:
    """
    Calibrates the base estimate using historical deviations.

    Logic: if similar projects deviated 35% on average,
    the base estimate is adjusted 35% upward. Percentiles
    are calculated from the actual distribution of deviations.
    """
    if len(proyectos_referencia) < 3:
        confianza = "baja"
    elif len(proyectos_referencia) < 7:
        confianza = "media"
    else:
        confianza = "alta"

    # Extract actual deviation ratios
    ratios = [p.ratio_desviacion for p in proyectos_referencia]

    ratio_medio = statistics.mean(ratios)
    ratio_mediana = statistics.median(ratios)

    # Adjust base estimate by historical bias
    # We use the median (more resistant to outliers than the mean)
    horas_calibrada = horas_base * ratio_mediana

    # Calculate percentiles for confidence interval
    ratios_ordenados = sorted(ratios)
    n = len(ratios_ordenados)

    def percentil(datos, p):
        k = (len(datos) - 1) * p / 100
        f = int(k)
        c = f + 1 if f + 1 < len(datos) else f
        d = k - f
        return datos[f] + d * (datos[c] - datos[f])

    p10 = horas_base * percentil(ratios_ordenados, 10)
    p50 = horas_base * percentil(ratios_ordenados, 50)
    p90 = horas_base * percentil(ratios_ordenados, 90)

    # Identify risk factors from projects that deviated most
    factores = []
    for p in proyectos_referencia:
        if p.ratio_desviacion > 1.3 and p.factores_desviacion:
            factores.append(
                f"{p.nombre}: {p.factores_desviacion}"
            )

    return EstimacionCalibrada(
        horas_base=horas_base,
        horas_calibrada=round(horas_calibrada, 0),
        intervalo_p10=round(p10, 0),
        intervalo_p50=round(p50, 0),
        intervalo_p90=round(p90, 0),
        confianza=confianza,
        n_proyectos_referencia=n,
        ratio_desviacion_medio=round(ratio_medio, 2),
        factores_riesgo=factores
    )

# --- Block 5 ---

PLANTILLA_ESTIMACION = """
I need to estimate the effort for the following consulting project:

## Project context
- **Service type**: {tipo_servicio}
- **Client sector**: {sector}
- **Regulatory complexity**: {complejidad}
- **Technologies in scope**: {tecnologias}
- **Planned team size**: {equipo} consultants

## Scope description
{descripcion_alcance}

## Known constraints
{restricciones}

## My initial estimate (uncalibrated)
{horas_base} hours, {duracion_semanas} weeks

## What I need
1. Similar historical projects with their actual deviation.
2. Calibrated estimate with P10-P50-P90 interval.
3. Risk factors specific to this project.
4. Recommendation on where to add buffer.
"""

# --- Block 6 ---

def cerrar_proyecto_y_actualizar(
    proyecto_id: str,
    horas_reales: float,
    duracion_real: int,
    equipo_real: int,
    factores_desviacion: str | None = None
) -> dict:
    """When closing a project, updates the historical base
    and recalculates calibration metrics."""
    proyecto = obtener_proyecto(proyecto_id)

    # Update actual data
    proyecto.horas_reales = horas_reales
    proyecto.duracion_semanas_real = duracion_real
    proyecto.equipo_real = equipo_real
    proyecto.ratio_desviacion = horas_reales / proyecto.horas_estimadas
    proyecto.factores_desviacion = factores_desviacion

    guardar_proyecto(proyecto)

    # Recalculate global calibration metrics
    todos = obtener_todos_proyectos()
    ratios = [p.ratio_desviacion for p in todos if p.horas_reales > 0]

    metricas = {
        "n_proyectos": len(ratios),
        "ratio_medio": round(statistics.mean(ratios), 2),
        "ratio_mediano": round(statistics.median(ratios), 2),
        "mejora_ultimo_anio": calcular_tendencia(todos),
    }

    return metricas

# --- Block 7 ---

FACTORES_RIESGO = {
    "cliente_nuevo": 1.15,        # +15%: no prior history
    "equipo_junior": 1.20,        # +20%: >40% of team is junior
    "tecnologia_nueva": 1.25,     # +25%: technology not used before
    "multi_framework": 1.10,      # +10%: more than one regulatory framework
    "dependencia_tercero": 1.15,  # +15%: external dependency
    "alcance_difuso": 1.30,       # +30%: requirements not finalized
    "plazo_agresivo": 1.10,       # +10%: duration < 70% of average
    "distribucion_geografica": 1.10,  # +10%: >2 client sites
}

def aplicar_factores_riesgo(
    estimacion: EstimacionCalibrada,
    factores_activos: list[str]
) -> EstimacionCalibrada:
    """Adjusts the calibrated estimate with additional risk factors."""
    multiplicador = 1.0
    for factor in factores_activos:
        if factor in FACTORES_RIESGO:
            multiplicador *= FACTORES_RIESGO[factor]

    # Apply compound multiplier (capped at 2.0x to prevent
    # absurd estimates with many accumulated factors)
    multiplicador = min(multiplicador, 2.0)

    return EstimacionCalibrada(
        horas_base=estimacion.horas_base,
        horas_calibrada=round(
            estimacion.horas_calibrada * multiplicador, 0
        ),
        intervalo_p10=round(estimacion.intervalo_p10 * multiplicador, 0),
        intervalo_p50=round(estimacion.intervalo_p50 * multiplicador, 0),
        intervalo_p90=round(estimacion.intervalo_p90 * multiplicador, 0),
        confianza=estimacion.confianza,
        n_proyectos_referencia=estimacion.n_proyectos_referencia,
        ratio_desviacion_medio=round(
            estimacion.ratio_desviacion_medio * multiplicador, 2
        ),
        factores_riesgo=estimacion.factores_riesgo + factores_activos
    )
