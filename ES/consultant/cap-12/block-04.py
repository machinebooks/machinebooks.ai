# Extraído de: LibroConsultor/cap-12-auditorias-automatizadas.md
@dataclass
class EvidenceRecord:
    """Registro de evidencia vinculado a un hallazgo."""
    evidence_id: str
    source_document: str
    page_or_section: str
    quote: str
    timestamp_analyzed: str
    control_ids: list[str] = field(default_factory=list)

class EvidenceCollector:
    """Recolector y organizador de evidencias de auditoría."""

    def __init__(self):
        self.records: list[EvidenceRecord] = []

    def collect_from_evaluation(
        self, control: AuditControl, doc_name: str, quotes: list[str]
    ):
        """Registra evidencias encontradas durante la evaluación."""
        from datetime import datetime
        for i, quote in enumerate(quotes):
            record = EvidenceRecord(
                evidence_id=f"EV-{len(self.records)+1:04d}",
                source_document=doc_name,
                page_or_section=self._locate_section(quote, doc_name),
                quote=quote[:500],  # Limitar longitud de cita
                timestamp_analyzed=datetime.now().isoformat(),
                control_ids=[control.control_id]
            )
            self.records.append(record)

    def generate_evidence_matrix(self) -> dict:
        """Genera matriz de trazabilidad control-evidencia."""
        matrix = {}
        for record in self.records:
            for ctrl_id in record.control_ids:
                if ctrl_id not in matrix:
                    matrix[ctrl_id] = []
                matrix[ctrl_id].append({
                    "evidence_id": record.evidence_id,
                    "document": record.source_document,
                    "quote_preview": record.quote[:100] + "..."
                })
        return matrix
