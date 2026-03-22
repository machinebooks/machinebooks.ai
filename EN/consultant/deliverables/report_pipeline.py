# Source: The Consultant and the Machine -- Chapter 14
# Pattern: Full reporting: findings, export (Word/PPT/PDF), continuous
from dataclasses import dataclass, field
from enum import Enum

class Severidad(Enum):
    CRITICA = "critica"
    ALTA = "alta"
    MEDIA = "media"
    BAJA = "baja"
    INFORMATIVA = "informativa"

class Prioridad(Enum):
    INMEDIATA = "inmediata"       # 0-30 days
    CORTO_PLAZO = "corto_plazo"  # 1-3 months
    MEDIO_PLAZO = "medio_plazo"  # 3-12 months
    LARGO_PLAZO = "largo_plazo"  # 12+ months

@dataclass
class Hallazgo:
    id: str
    titulo: str
    descripcion: str
    evidencia: str
    severidad: Severidad
    area: str  # "security", "architecture", "costs", etc.
    impacto_negocio: str
    recomendacion: str
    prioridad: Prioridad
    esfuerzo_estimado: str  # "2 weeks", "3 months", etc.
    coste_estimado: str | None = None
    referencias: list[str] = field(default_factory=list)

@dataclass
class ProyectoReporting:
    nombre_proyecto: str
    cliente: str  # Always anonymized
    tipo: str     # "audit", "gap_analysis", "architecture"
    fecha_inicio: str
    fecha_fin: str
    alcance: str
    hallazgos: list[Hallazgo] = field(default_factory=list)
    contexto_adicional: str = ""

# --- Block 2 ---

VOICE_PROMPT = """You are a technical consulting writer with these style rules:

TONE:
- Direct and quantitative. Every assertion must have a data point or evidence.
- Prescriptive in recommendations: "migrate X before Y" instead of
  "it is recommended to consider migrating X."
- No weak adverbs: eliminate "basically," "simply," "very."
- No unnecessary passive voice: "the system processes" instead of
  "data is processed by the system."

FINDING STRUCTURE:
- First sentence: what was observed (fact).
- Second sentence: why it matters (business impact).
- Third sentence: what must be done (action).
- Quantitative data whenever available.

RECOMMENDATION STRUCTURE:
- Imperative verb: "implement," "migrate," "configure," "eliminate."
- Concrete deadline: "before June 2026," not "in the short term."
- Cost or effort estimate when available.
- Consequence of inaction: "each month of delay costs €X in Y."

PROHIBITIONS:
- Don't use "it is recommended to consider." Recommend directly.
- Don't use empty jargon: "synergy," "holistic," "best-in-class."
- Don't invent data. If there's no data, omit the quantification.
- Don't make judgments about the client's people or teams.

LANGUAGE: technical Spanish from Spain. "Coste," not "costo."
"Ordenador," not "computadora."
"""

# --- Block 3 ---

import anthropic

client = anthropic.Anthropic(api_key="<YOUR_API_KEY>")

def generar_narrativa_hallazgo(
    hallazgo: Hallazgo,
    contexto_proyecto: str,
    voice_prompt: str
) -> str:
    """Generates the narrative for an individual finding."""

    prompt_usuario = f"""Write the narrative for this consulting finding.

FINDING:
- Title: {hallazgo.titulo}
- Technical description: {hallazgo.descripcion}
- Evidence: {hallazgo.evidencia}
- Severity: {hallazgo.severidad.value}
- Area: {hallazgo.area}
- Business impact: {hallazgo.impacto_negocio}

PROJECT CONTEXT:
{contexto_proyecto}

INSTRUCTIONS:
1. Write 2-4 paragraphs narrating the finding.
2. Open with the observed fact, not the recommendation.
3. Connect to business impact in the second paragraph.
4. If there are quantitative data in the evidence, include them.
5. Close with the implication, not the solution
   (the solution goes in Recommendations).
6. Length: 150-250 words."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=voice_prompt,
        messages=[{"role": "user", "content": prompt_usuario}]
    )
    return response.content[0].text

# --- Block 4 ---

import subprocess

def exportar_word(
    markdown_path: str,
    output_path: str,
    reference_docx: str
) -> str:
    """Converts Markdown to Word using corporate styles."""
    cmd = [
        "pandoc",
        markdown_path,
        "-o", output_path,
        f"--reference-doc={reference_docx}",
        "--toc",
        "--toc-depth=3",
        "--number-sections",
        "--metadata", "lang=es-ES",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"Pandoc failed: {result.stderr}")
    return output_path
