# Extraído de: LibroConsultor/cap-29-futuro-consultor.md
from dataclasses import dataclass
from typing import List
import anthropic

@dataclass
class ServicioConsultoria:
    nombre: str
    horas_humanas_sin_ia: float     # Horas antes de IA
    horas_humanas_con_ia: float     # Horas con agentes
    coste_ia_por_proyecto: float    # Coste de tokens/APIs
    precio_cliente: float           # Lo que cobra al cliente
    requiere_senior: bool           # ¿Necesita perfil senior?

def calcular_apalancamiento(servicio: ServicioConsultoria) -> dict:
    """Calcula métricas de apalancamiento para un servicio."""
    reduccion_tiempo = 1 - (servicio.horas_humanas_con_ia /
                            servicio.horas_humanas_sin_ia)
    coste_hora_consultor = 85.0  # €/hora coste interno (escalado)

    coste_sin_ia = servicio.horas_humanas_sin_ia * coste_hora_consultor
    coste_con_ia = (servicio.horas_humanas_con_ia * coste_hora_consultor
                    + servicio.coste_ia_por_proyecto)

    margen_sin_ia = servicio.precio_cliente - coste_sin_ia
    margen_con_ia = servicio.precio_cliente - coste_con_ia

    # Apalancamiento = valor entregado / horas humanas invertidas
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
