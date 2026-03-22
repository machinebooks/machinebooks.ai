# Extraído de: LibroConsultor/cap-10-estimacion-esfuerzos.md
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
    """Registro de un proyecto completado con datos reales."""
    id: str
    nombre: str  # anonimizado: "Auditoría ENS sector público 2024"
    descripcion_alcance: str  # texto libre para búsqueda semántica
    tipo_servicio: TipoServicio
    sector: str
    complejidad_regulatoria: ComplejidadRegulatoria
    tecnologias: list[str]
    # Estimación original
    horas_estimadas: float
    duracion_semanas_estimada: int
    equipo_estimado: int  # número de consultores
    # Resultado real
    horas_reales: float
    duracion_semanas_real: int
    equipo_real: int
    # Métricas derivadas
    ratio_desviacion: float = Field(
        default=0.0,
        description="horas_reales / horas_estimadas"
    )
    factores_desviacion: Optional[str] = None  # qué causó la desviación
    fecha_cierre: str  # formato YYYY-MM
