# Extraído de: LibroConsultor/cap-26-caso-seguridad.md
from anthropic import Anthropic
from dataclasses import dataclass

client = Anthropic()

@dataclass
class ControlMapping:
    iso_control: str          # e.g., "A.8.1 - User endpoint devices"
    ens_measures: list[str]   # e.g., ["mp.eq.1", "mp.eq.2"]
    status: str               # "compliant", "partial", "non_compliant"
    evidence_refs: list[str]  # documentos que lo soportan
    gap_description: str      # brecha identificada (vacío si cumple)
    recommendation: str       # acción correctiva sugerida
    priority: str             # "critical", "high", "medium", "low"

def cross_reference_controls(
    iso_findings: list[dict],
    ens_mapping_table: dict
) -> list[ControlMapping]:
    """Cruza hallazgos ISO contra medidas ENS usando contexto
    normativo cargado en el prompt de sistema."""

    prompt = f"""Con base en los hallazgos de auditoría ISO 27001
    proporcionados, genera el mapeo cruzado contra ENS categoría alta.

    Para cada control ISO con estado 'parcial' o 'no conforme':
    1. Identifica las medidas ENS afectadas
    2. Evalúa si la brecha ISO implica brecha ENS
    3. Prioriza: critical si afecta a disponibilidad de servicios
       esenciales, high si afecta a confidencialidad de datos
       personales, medium/low en caso contrario

    Hallazgos ISO:
    {json.dumps(iso_findings, ensure_ascii=False, indent=2)}

    Tabla de mapeo ISO-ENS:
    {json.dumps(ens_mapping_table, ensure_ascii=False, indent=2)}"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8192,
        messages=[{"role": "user", "content": prompt}]
    )
    # Parsear y validar la respuesta estructurada
    return parse_control_mappings(response.content[0].text)
