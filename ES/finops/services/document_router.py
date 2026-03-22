# Extraído de: LibroFinOps/cap-25-caso-tokens.md
# services/document_router.py
# Router que asigna el modelo correcto a cada operación documental.
# Único punto de decisión de modelo en toda la plataforma.

from enum import Enum
from dataclasses import dataclass


class OperacionDocumental(str, Enum):
    CLASIFICACION = "clasificacion"
    EXTRACCION_ENTIDADES = "extraccion_entidades"
    RESUMEN_EJECUTIVO = "resumen_ejecutivo"
    RECOMENDACION_ACCION = "recomendacion_accion"


class ComplejidadDocumento(str, Enum):
    SIMPLE = "simple"      # Estructura conocida
    MEDIO = "medio"        # Algunas ambigüedades
    COMPLEJO = "complejo"  # Lenguaje denso, múltiples partes


@dataclass
class DecisionModelo:
    modelo: str
    razon: str
    coste_est_eur: float
