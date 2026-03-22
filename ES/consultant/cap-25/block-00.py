# Extraído de: LibroConsultor/cap-25-confianza-cliente.md
from anthropic import Anthropic
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

class TransparencyStatus(Enum):
    COMPLIANT = "compliant"
    WARNING = "warning"
    NON_COMPLIANT = "non_compliant"

@dataclass
class TransparencyCheck:
    has_methodology_note: bool
    has_reviewer_attribution: bool
    has_unedited_ai_patterns: bool
    raw_output_sections: list[str]
    status: TransparencyStatus

def audit_deliverable_transparency(
    document_path: str,
    reviewer_name: str
) -> TransparencyCheck:
    """Audita un entregable para verificar cumplimiento
    del protocolo de transparencia antes del envío."""

    client = Anthropic()
    content = Path(document_path).read_text(encoding="utf-8")

    # Verificación 1: nota metodológica presente
    methodology_prompt = f"""Analiza este documento de consultoría.
    ¿Contiene una nota metodológica que declare el uso de
    herramientas de IA? Responde solo 'sí' o 'no'.

    Documento (primeros 2000 caracteres del final):
    {content[-2000:]}"""

    resp_method = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=10,
        messages=[{"role": "user", "content": methodology_prompt}]
    )
    has_note = "sí" in resp_method.content[0].text.lower()

    # Verificación 2: atribución de revisor
    has_reviewer = reviewer_name.lower() in content.lower()

    # Verificación 3: patrones de output sin editar
    pattern_prompt = f"""Analiza este documento de consultoría.
    Identifica secciones que parezcan output directo de un LLM
    sin edición humana significativa. Indicadores: frases
    genéricas sin datos del cliente, estructura excesivamente
    uniforme, ausencia de matices específicos del contexto.

    Devuelve una lista JSON de títulos de sección sospechosos.
    Si no hay secciones sospechosas, devuelve [].

    Documento:
    {content[:8000]}"""

    resp_patterns = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": pattern_prompt}]
    )

    import json
    try:
        raw_sections = json.loads(resp_patterns.content[0].text)
    except json.JSONDecodeError:
        raw_sections = []

    # Determinar estado
    if not has_note or not has_reviewer:
        status = TransparencyStatus.NON_COMPLIANT
    elif len(raw_sections) > 0:
        status = TransparencyStatus.WARNING
    else:
        status = TransparencyStatus.COMPLIANT

    return TransparencyCheck(
        has_methodology_note=has_note,
        has_reviewer_attribution=has_reviewer,
        has_unedited_ai_patterns=len(raw_sections) > 0,
        raw_output_sections=raw_sections,
        status=status
    )
