# Extraído de: LibroConsultor/cap-15-madurez-ia.md
import anthropic
from dataclasses import dataclass, field
from enum import Enum

class Dimension(str, Enum):
    STRATEGY = "estrategia"
    DATA = "datos"
    TECHNOLOGY = "tecnologia"
    PEOPLE = "personas"
    GOVERNANCE = "gobernanza"

@dataclass
class AssessmentQuestion:
    id: str
    dimension: Dimension
    text: str
    stakeholder_profiles: list[str]  # CIO, CDO, negocio, IT, etc.
    evidence_required: bool = False
    follow_ups: list[str] = field(default_factory=list)

# Catálogo parcial — el real tiene 85 preguntas
QUESTION_CATALOG = [
    AssessmentQuestion(
        id="STR-01",
        dimension=Dimension.STRATEGY,
        text="¿Existe un documento de estrategia de IA aprobado "
             "por la dirección? ¿Quién lo elaboró y cuándo?",
        stakeholder_profiles=["CIO", "CEO", "CDO"],
        evidence_required=True,
        follow_ups=[
            "¿Se revisa periódicamente? ¿Con qué frecuencia?",
            "¿Tiene presupuesto asignado o es declarativo?",
            "¿Qué métricas de éxito define?"
        ]
    ),
    AssessmentQuestion(
        id="DAT-01",
        dimension=Dimension.DATA,
        text="¿Disponen de un catálogo de datos actualizado? "
             "¿Qué porcentaje de sus fuentes de datos están documentadas?",
        stakeholder_profiles=["CDO", "CIO", "IT"],
        evidence_required=True,
        follow_ups=[
            "¿Tienen métricas de calidad de datos automatizadas?",
            "¿Cuánto tiempo tarda un equipo nuevo en acceder "
             "a los datos que necesita?"
        ]
    ),
    AssessmentQuestion(
        id="PER-01",
        dimension=Dimension.PEOPLE,
        text="¿Cuántas personas en la organización trabajan con IA "
             "como actividad principal? ¿Y como actividad secundaria?",
        stakeholder_profiles=["CIO", "RRHH", "CDO"],
        evidence_required=False,
        follow_ups=[
            "¿Existe un programa de formación en IA? ¿Quién participa?",
            "¿Se han incorporado perfiles de ML/datos en los últimos "
             "12 meses? ¿Cuántos?"
        ]
    ),
]
