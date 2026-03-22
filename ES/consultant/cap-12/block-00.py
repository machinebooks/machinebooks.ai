# Extraído de: LibroConsultor/cap-12-auditorias-automatizadas.md
import anthropic
import json
from pathlib import Path
from dataclasses import dataclass, field

@dataclass
class AuditControl:
    """Representa un control del marco de referencia."""
    control_id: str
    title: str
    description: str
    category: str
    # Resultado de la evaluación
    status: str = "pendiente"  # cumple | no_cumple | parcial | no_aplica
    evidence_refs: list[str] = field(default_factory=list)
    justification: str = ""
    finding: dict | None = None

@dataclass
class AuditFinding:
    """Hallazgo de auditoría estructurado."""
    finding_id: str
    control_id: str
    severity: str  # alta | media | baja | observación
    title: str
    description: str
    evidence_quote: str  # Cita textual verificable
    risk: str
    recommendation: str
    compensating_controls: str = ""

class AuditAgent:
    """Agente de auditoría que evalúa controles contra evidencias."""

    def __init__(self, framework: str, model: str = "claude-sonnet-4-6"):
        self.client = anthropic.Anthropic()
        self.model = model
        self.framework = framework
        self.controls: list[AuditControl] = []
        self.findings: list[AuditFinding] = []
        self.documents: dict[str, str] = {}  # nombre -> contenido

    def load_framework(self, controls_path: str):
        """Carga los controles del marco de referencia."""
        with open(controls_path, "r") as f:
            raw_controls = json.load(f)
        self.controls = [
            AuditControl(**ctrl) for ctrl in raw_controls
        ]
        print(f"Cargados {len(self.controls)} controles de {self.framework}")
