# Extraído de: LibroConsultor/cap-13-gap-analysis.md
from pathlib import Path


class EvidenceProcessor:
    """Procesa documentación del cliente y extrae hechos."""

    def __init__(self):
        self.client = anthropic.Anthropic()
        self.evidence_index: dict[str, list[str]] = {}

    def process_document(
        self, doc_path: str, doc_type: str = "policy"
    ) -> dict:
        """Extrae hechos relevantes de un documento."""
        content = self._read_document(doc_path)

        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system="""Eres un analista de compliance. Extrae
hechos objetivos del documento: qué existe, quién lo aprobó,
cuándo se revisó, qué cubre, qué excluye. NO evalúes ni
opines. Solo extrae hechos verificables.""",
            messages=[{"role": "user", "content": f"""
Tipo de documento: {doc_type}
Contenido:
{content[:12000]}

Extrae hechos en formato estructurado:
- fecha_aprobacion: si se menciona
- alcance: qué cubre el documento
- responsable: quién es responsable
- revision: fecha de última revisión
- hechos_relevantes: lista de hechos concretos
- controles_relacionados: qué controles ISO/ENS podría cubrir
- lagunas_detectadas: qué áreas omite el documento"""}],
        )
        facts = self._parse_facts(response)
        # Indexar hechos por controles potencialmente relacionados
        for control_id in facts.get("controles_relacionados", []):
            self.evidence_index.setdefault(
                control_id, []
            ).append(facts)
        return facts

    def get_evidence_for_control(
        self, control_id: str
    ) -> str:
        """Obtiene evidencias indexadas para un control."""
        evidence_items = self.evidence_index.get(
            control_id, []
        )
        if not evidence_items:
            return "No se encontraron evidencias documentales."
        # Consolidar y resumir evidencias relevantes
        return self._summarize_evidence(evidence_items)
