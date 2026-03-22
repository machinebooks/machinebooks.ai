# Extraído de: LibroConsultor/cap-02-anatomia-proyecto.md
from dataclasses import dataclass, field
from enum import Enum

class Phase(Enum):
    PRESALES = "preventa"
    DELIVERY = "entrega"
    KNOWLEDGE = "captura_conocimiento"

class AutomationPotential(Enum):
    HIGH = "alto"
    MEDIUM = "medio"
    LOW = "bajo"
    NONE = "ninguno"

@dataclass
class Activity:
    """Representa una actividad dentro de un proyecto de consultoría."""
    name: str
    phase: Phase
    hours_manual: float          # Horas estimadas sin IA
    hours_assisted: float        # Horas estimadas con IA
    automation_potential: AutomationPotential
    requires_client_interaction: bool
    requires_expert_judgment: bool
    frequency_per_project: int   # Veces que se ejecuta por proyecto
    description: str = ""

@dataclass
class ConsultingProject:
    """Modelo estructurado de un proyecto de consultoría."""
    name: str
    client_sector: str
    frameworks: list[str]        # ISO 27001, ENS, DORA, etc.
    duration_weeks: int
    team_size: int
    activities: list[Activity] = field(default_factory=list)

    @property
    def total_hours_manual(self) -> float:
        return sum(
            a.hours_manual * a.frequency_per_project
            for a in self.activities
        )

    @property
    def total_hours_assisted(self) -> float:
        return sum(
            a.hours_assisted * a.frequency_per_project
            for a in self.activities
        )

    @property
    def reduction_percentage(self) -> float:
        if self.total_hours_manual == 0:
            return 0.0
        return (1 - self.total_hours_assisted / self.total_hours_manual) * 100
