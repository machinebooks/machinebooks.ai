# Extraído de: LibroConsultor/cap-13-gap-analysis.md
import anthropic
import yaml
from pathlib import Path


class GapAnalysisAgent:
    """Agente de gap analysis multi-framework."""

    def __init__(self, org_profile: str, target_level: MaturityLevel):
        self.client = anthropic.Anthropic()
        self.org_profile = org_profile
        self.target_level = target_level
        self.frameworks: dict[str, list[Control]] = {}
        self.criteria: dict[str, EvaluationCriteria] = {}
        self.findings: list[GapFinding] = []

    def load_framework(self, yaml_path: str) -> None:
        """Carga un framework normativo desde YAML."""
        data = yaml.safe_load(Path(yaml_path).read_text())
        controls = []
        for c in data["controls"]:
            control = Control(
                framework=data["framework"],
                control_id=c["id"],
                title=c["title"],
                description=c["description"],
                category=c.get("category", "General"),
                cross_references=c.get("cross_references", []),
            )
            controls.append(control)
        self.frameworks[data["framework"]] = controls

    def evaluate_control(
        self, control: Control, evidence_text: str
    ) -> GapFinding:
        """Evalúa un control contra las evidencias del cliente."""
        criteria = self.criteria.get(
            f"{control.control_id}:{self.org_profile}"
        )
        criteria_text = self._format_criteria(criteria)

        prompt = f"""Evalúa el siguiente control normativo contra
las evidencias del cliente.

CONTROL: {control.framework} {control.control_id}
— {control.title}
Descripción: {control.description}

PERFIL DE ORGANIZACIÓN: {self.org_profile}

CRITERIOS DE EVALUACIÓN POR NIVEL:
{criteria_text}

EVIDENCIAS DEL CLIENTE:
{evidence_text}

Responde en JSON con estos campos:
- current_level: nivel actual (0-4)
- gap_description: qué falta para alcanzar nivel {self.target_level.value}
- remediation: acciones concretas recomendadas
- effort_days: estimación de esfuerzo en días-persona
- priority: "critica", "alta", "media" o "baja"
- confidence: confianza en la evaluación (0.0-1.0)
- reasoning: razonamiento paso a paso de la evaluación"""

        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            system="""Eres un auditor experto en normativa de
seguridad y compliance. Evalúas controles de forma rigurosa
pero justa. Si la evidencia es insuficiente para evaluar,
indica confidence baja. Nunca asumas cumplimiento sin
evidencia. Nunca exageres gaps sin justificación.""",
            messages=[{"role": "user", "content": prompt}],
        )
        return self._parse_finding(control, response)
