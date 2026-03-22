# Source: The FinOps Engineer and the Machine -- Chapter 25
# Pattern: Document routing by operation type

# services/document_router.py
# Router that assigns the correct model to each document operation.
# Single model decision point across the entire platform.

from enum import Enum
from dataclasses import dataclass


class OperacionDocumental(str, Enum):
    CLASIFICACION = "clasificacion"
    EXTRACCION_ENTIDADES = "extraccion_entidades"
    RESUMEN_EJECUTIVO = "resumen_ejecutivo"
    RECOMENDACION_ACCION = "recomendacion_accion"


class ComplejidadDocumento(str, Enum):
    SIMPLE = "simple"      # Known structure
    MEDIO = "medio"        # Some ambiguities
    COMPLEJO = "complejo"  # Dense language, multiple parties


@dataclass
class DecisionModelo:
    modelo: str
    razon: str
    coste_est_eur: float
