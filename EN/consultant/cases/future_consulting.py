# Source: The Consultant and the Machine -- Chapter 29
# Pattern: Future: team leverage, continuous advisory
from dataclasses import dataclass
from typing import List
import anthropic

@dataclass
class ServicioConsultoria:
    nombre: str
    horas_humanas_sin_ia: float     # Hours before AI
    horas_humanas_con_ia: float     # Hours with agents
    coste_ia_por_proyecto: float    # Token/API cost
    precio_cliente: float           # Client price
    requiere_senior: bool           # Needs senior profile?

def calcular_apalancamiento(servicio: ServicioConsultoria) -> dict:
    """Calculates leverage metrics for a service."""
    reduccion_tiempo = 1 - (servicio.horas_humanas_con_ia /
                            servicio.horas_humanas_sin_ia)
    coste_hora_consultor = 85.0  # €/hour internal cost (scaled)

    coste_sin_ia = servicio.horas_humanas_sin_ia * coste_hora_consultor
    coste_con_ia = (servicio.horas_humanas_con_ia * coste_hora_consultor
                    + servicio.coste_ia_por_proyecto)

    margen_sin_ia = servicio.precio_cliente - coste_sin_ia
    margen_con_ia = servicio.precio_cliente - coste_con_ia

    # Leverage = value delivered / human hours invested
    apalancamiento = servicio.precio_cliente / servicio.horas_humanas_con_ia

    return {
        "servicio": servicio.nombre,
        "reduccion_tiempo": f"{reduccion_tiempo:.0%}",
        "margen_sin_ia": f"€{margen_sin_ia:,.0f}",
        "margen_con_ia": f"€{margen_con_ia:,.0f}",
        "mejora_margen": f"{((margen_con_ia/margen_sin_ia)-1):.0%}",
        "apalancamiento_eur_hora": f"€{apalancamiento:,.0f}",
        "candidato_productizar": reduccion_tiempo > 0.6
    }

# --- Block 2 ---

from claude_agent_sdk import Agent, tool
import anthropic
from datetime import datetime

@tool
def evaluar_postura_seguridad(cliente_id: str) -> dict:
    """Evaluates the client's current security posture
    against the agreed reference framework."""
    evidencias = obtener_evidencias_cliente(cliente_id)
    controles = obtener_framework_cliente(cliente_id)

    client = anthropic.Anthropic()
    evaluacion = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system="""You are a security auditor. Evaluate each control
        against the provided evidence. Classify:
        compliant / partially_compliant / non_compliant / no_evidence.
        For non_compliant, indicate risk (high/medium/low) and
        a concrete corrective action with estimated timeline.""",
        messages=[{
            "role": "user",
            "content": f"Controls: {controles}\nEvidence: {evidencias}"
        }]
    )
    return {"evaluacion": evaluacion.content, "fecha": datetime.now().isoformat()}

@tool
def generar_alerta_si_necesaria(evaluacion: dict,
                                 umbral_riesgo: str = "alto") -> dict:
    """Generates an alert only if there are non-compliant controls
    with risk equal to or above the threshold."""
    ...
