# Extraído de: LibroFinOps/cap-29-convergencia.md
# models/unified_cost_event.py
# Modelo unificado de evento de coste que integra las cuatro dimensiones:
# tokens/IA, cloud, personas y huella energética.

from datetime import datetime
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional


class DimensionCoste(str, Enum):
    TOKENS_LLM = "tokens_llm"         # Gasto en APIs de LLM
    CLOUD_COMPUTE = "cloud_compute"   # Instancias, contenedores, funciones
    CLOUD_STORAGE = "cloud_storage"   # S3, blob, GCS
    CLOUD_NETWORK = "cloud_network"   # Data transfer, CDN
    PERSONAS = "personas"             # Tiempo de equipo imputado
    HERRAMIENTAS = "herramientas"     # Licencias SaaS, APIs externas


@dataclass
class HuellaEnergetica:
    """Estimación de impacto energético asociado a un evento de coste."""
    kwh_estimados: float        # Kilovatios-hora consumidos
    co2_gramos: float           # Gramos de CO₂ equivalente
    fuente_energia: str         # "renovable", "mixta", "fosil", "desconocida"
    factor_emision: float       # gCO₂/kWh del proveedor/región


@dataclass
class UnifiedCostEvent:
    """
    Evento de coste unificado: una unidad de gasto en cualquiera de
    las cuatro dimensiones del FinOps convergente.
    """
    id: str
    timestamp: datetime
    dimension: DimensionCoste
    proyecto_codigo: str
    equipo_codigo: str
    servicio: str
    entorno: str  # "produccion", "staging", "desarrollo"
    coste_eur: Decimal
    huella: Optional[HuellaEnergetica] = None
    meta: dict = field(default_factory=dict)

    @property
    def co2_gramos(self) -> float:
        return self.huella.co2_gramos if self.huella else 0.0
