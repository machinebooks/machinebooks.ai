# Extraído de: LibroConsultor/cap-18-onboarding.md
from dataclasses import dataclass, field
from enum import Enum

class ContentCategory(Enum):
    METHODOLOGY = "methodology"          # Cómo hacemos las cosas
    STANDARDS = "standards"              # Qué normas aplicamos
    TEMPLATES = "templates"              # Formatos de entregables
    CASE_STUDIES = "case_studies"        # Ejemplos de proyectos pasados
    TOOLS = "tools"                      # Herramientas y configuraciones
    CLIENT_PROTOCOLS = "client_protocols"  # Protocolos de interacción con clientes

class DifficultyLevel(Enum):
    FOUNDATIONAL = 1    # Lo que necesitas saber la primera semana
    INTERMEDIATE = 2    # Lo que necesitas para tu primera tarea
    ADVANCED = 3        # Lo que necesitas para trabajar sin supervisión

@dataclass
class OnboardingDocument:
    """Documento indexado para el programa de onboarding."""
    doc_id: str
    title: str
    category: ContentCategory
    difficulty: DifficultyLevel
    summary: str                              # Resumen de 2-3 frases
    prerequisites: list[str] = field(default_factory=list)  # IDs de docs previos
    estimated_read_time_min: int = 10
    last_updated: str = ""                    # Fecha de última revisión
    verified_by: str = ""                     # Senior que validó el contenido
