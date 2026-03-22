# Extraído de: LibroConsultor/cap-16-roadmaps-ia.md
import anthropic
from dataclasses import dataclass, field
from enum import Enum

class Horizonte(Enum):
    QUICK_WIN = "0-90 días"
    CONSOLIDACION = "3-12 meses"
    TRANSFORMACION = "12-36 meses"

class TipoAdquisicion(Enum):
    BUILD = "build"
    BUY = "buy"
    INTEGRATE = "integrate"

@dataclass
class Iniciativa:
    nombre: str
    descripcion: str
    horizonte: Horizonte
    impacto: int          # 1-5
    esfuerzo: int         # 1-5
    dependencias: list[str] = field(default_factory=list)
    riesgo: int = 3       # 1-5
    tipo: TipoAdquisicion = TipoAdquisicion.INTEGRATE
    presupuesto_min: float = 0.0
    presupuesto_max: float = 0.0
    equipo_necesario: list[str] = field(default_factory=list)
    kpi_exito: str = ""

    @property
    def prioridad(self) -> float:
        """Puntuación compuesta de priorización."""
        n_deps = len(self.dependencias)
        return (self.impacto * 3
                - self.esfuerzo * 2
                - min(n_deps, 3) * 2
                - self.riesgo) / 8
