# Source: The FinOps Engineer and the Machine -- Chapter 29
# Pattern: Unified cost event model (tokens + cloud + carbon)

# models/unified_cost_event.py
# Unified cost event model that integrates the four dimensions:
# tokens/AI, cloud, people and energy footprint.

from datetime import datetime
from decimal import Decimal
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional


class DimensionCoste(str, Enum):
    TOKENS_LLM = "tokens_llm"         # LLM API spend
    CLOUD_COMPUTE = "cloud_compute"   # Instances, containers, functions
    CLOUD_STORAGE = "cloud_storage"   # S3, blob, GCS
    CLOUD_NETWORK = "cloud_network"   # Data transfer, CDN
    PERSONAS = "personas"             # Allocated team time
    HERRAMIENTAS = "herramientas"     # SaaS licenses, external APIs


@dataclass
class HuellaEnergetica:
    """Energy impact estimate associated with a cost event."""
    kwh_estimados: float        # Kilowatt-hours consumed
    co2_gramos: float           # Grams of CO2 equivalent
    fuente_energia: str         # "renewable", "mixed", "fossil", "unknown"
    factor_emision: float       # gCO2/kWh from the provider/region


@dataclass
class UnifiedCostEvent:
    """
    Unified cost event: a unit of spend in any of
    the four dimensions of convergent FinOps.
    """
    id: str
    timestamp: datetime
    dimension: DimensionCoste
    proyecto_codigo: str
    equipo_codigo: str
    servicio: str
    entorno: str  # "production", "staging", "development"
    coste_eur: Decimal
    huella: Optional[HuellaEnergetica] = None
    meta: dict = field(default_factory=dict)

    @property
    def co2_gramos(self) -> float:
        return self.huella.co2_gramos if self.huella else 0.0
