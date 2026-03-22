# Extraído de: LibroConsultor/cap-02-anatomia-proyecto.md
from dataclasses import dataclass
from enum import Enum

class ProjectStage(Enum):
    OPPORTUNITY = "oportunidad"
    PROPOSAL = "propuesta"
    DELIVERY = "entrega"
    CLOSURE = "cierre"
    KNOWLEDGE = "conocimiento_capturado"

@dataclass
class ProjectPipeline:
    """Orquesta el flujo completo de un proyecto de consultoría."""
    project_id: str
    stage: ProjectStage
    analysis: dict = None       # Resultado del agente de análisis
    proposal: dict = None       # Propuesta generada
    delivery_log: list = None   # Registro de entrega
    lessons: dict = None        # Lecciones aprendidas

    def advance_to_proposal(self, rfp_text: str):
        """Analiza la oportunidad y prepara el análisis para la propuesta."""
        self.analysis = analyze_project(rfp_text)
        self.stage = ProjectStage.PROPOSAL
        # El análisis alimenta la estimación de esfuerzos
        # y la generación de la propuesta técnica
        return self.analysis

    def advance_to_delivery(self):
        """Transiciona a entrega con el plan de automatización."""
        self.stage = ProjectStage.DELIVERY
        self.delivery_log = []
        # Las actividades identificadas como automatizables
        # se asignan a agentes; las humanas, a consultores

    def close_and_capture(self, feedback: dict):
        """Cierra el proyecto y captura conocimiento."""
        self.lessons = extract_lessons_learned(
            project_name=self.project_id,
            deliverables_summary=feedback.get("deliverables", ""),
            deviations=feedback.get("deviations", []),
            team_feedback=feedback.get("team", []),
            client_feedback=feedback.get("client", "")
        )
        self.stage = ProjectStage.KNOWLEDGE
        # Las lecciones se indexan para RAG
        # y alimentan estimaciones de proyectos futuros
        return self.lessons
