# Extraído de: LibroConsultor/cap-09-generacion-propuestas.md
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

class SeccionTipo(Enum):
    RESUMEN_EJECUTIVO = "resumen_ejecutivo"
    COMPRENSION_NECESIDAD = "comprension_necesidad"
    ENFOQUE_TECNICO = "enfoque_tecnico"
    METODOLOGIA = "metodologia"
    EQUIPO = "equipo"
    PLAN_TRABAJO = "plan_trabajo"
    # Pricing se excluye: es decisión humana

@dataclass
class ContextoPropuesta:
    """Contexto completo para generar una propuesta."""
    cliente: str                    # Descriptor anonimizado del cliente
    sector: str                     # Sector: publico, financiero, industria...
    tipo_servicio: str              # auditoria, consultoria, implantacion...
    requisitos_pliego: list[dict]   # Requisitos extraídos del análisis RFP
    criterios_valoracion: list[dict] # Criterios con ponderación
    restricciones: list[str]        # Plazos, certificaciones, ubicación...
    equipo_propuesto: list[dict]    # Decisión humana previa
    precio_objetivo: float          # Decisión humana previa
    fecha_entrega: datetime

@dataclass
class SeccionGenerada:
    tipo: SeccionTipo
    contenido: str
    version: int = 1
    score_quality: float = 0.0     # 0-100, estimación del quality gate
    revisado_por: str | None = None
    notas_revision: list[str] = field(default_factory=list)
    tokens_consumidos: int = 0
    coste_generacion: float = 0.0  # USD
