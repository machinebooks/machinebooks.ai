# Extraído de: LibroConsultor/cap-20-pricing.md
import anthropic
from dataclasses import dataclass, field

@dataclass
class ProyectoInput:
    """Parámetros de entrada para el cálculo de pricing."""
    tipo: str                    # "auditoria", "gap_analysis", "roadmap", "assessment"
    sector: str                  # "financiero", "publico", "energia", "salud"
    alcance: str                 # Descripción libre del alcance
    frameworks: list[str]        # ["ISO27001", "ENS", "NIS2", "DORA"]
    horas_estimadas_sin_ia: int  # Estimación tradicional
    factor_reduccion_ia: float   # 0.4 = 60% reducción
    valor_cliente_estimado: float  # Valor estimable del resultado para el cliente
    es_licitacion_publica: bool
    cliente_recurrente: bool
    num_retainers_activos: int = 0  # Para calcular viabilidad de suscripción

@dataclass
class PricingResult:
    """Resultado del cálculo de pricing."""
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
