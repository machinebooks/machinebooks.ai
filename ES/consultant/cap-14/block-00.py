# Extraído de: LibroConsultor/cap-14-reporting.md
from dataclasses import dataclass, field
from enum import Enum

class Severidad(Enum):
    CRITICA = "critica"
    ALTA = "alta"
    MEDIA = "media"
    BAJA = "baja"
    INFORMATIVA = "informativa"

class Prioridad(Enum):
    INMEDIATA = "inmediata"       # 0-30 días
    CORTO_PLAZO = "corto_plazo"  # 1-3 meses
    MEDIO_PLAZO = "medio_plazo"  # 3-12 meses
    LARGO_PLAZO = "largo_plazo"  # 12+ meses

@dataclass
class Hallazgo:
    id: str
    titulo: str
    descripcion: str
    evidencia: str
    severidad: Severidad
    area: str  # "seguridad", "arquitectura", "costes", etc.
    impacto_negocio: str
    recomendacion: str
    prioridad: Prioridad
    esfuerzo_estimado: str  # "2 semanas", "3 meses", etc.
    coste_estimado: str | None = None
    referencias: list[str] = field(default_factory=list)

@dataclass
class ProyectoReporting:
    nombre_proyecto: str
    cliente: str  # Siempre anonimizado
    tipo: str     # "auditoria", "gap_analysis", "arquitectura"
    fecha_inicio: str
    fecha_fin: str
    alcance: str
    hallazgos: list[Hallazgo] = field(default_factory=list)
    contexto_adicional: str = ""
