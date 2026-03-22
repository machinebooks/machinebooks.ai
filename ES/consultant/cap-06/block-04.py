# Extraído de: LibroConsultor/cap-06-generacion-entregables.md
from enum import Enum
from datetime import datetime

class ReviewStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    NEEDS_REVISION = "needs_revision"
    REJECTED = "rejected"

class QualityChecker:
    """Control de calidad con revisión humana obligatoria."""

    def __init__(self, template: dict):
        self.template = template
        self.reviews: dict[str, ReviewStatus] = {}
        self.automated_checks: list[dict] = []

    def run_automated_checks(self, document: str) -> list[dict]:
        """Verificaciones automáticas antes de revisión humana."""
        issues = []

        # Verificar extensión mínima por sección
        for section in self.template["sections"]:
            max_words = section.get("max_words")
            if max_words:
                actual = self._count_words_in_section(
                    document, section["id"]
                )
                if actual < max_words * 0.7:
                    issues.append({
                        "section": section["id"],
                        "type": "underfilled",
                        "detail": f"{actual} palabras vs "
                                  f"{max_words} objetivo",
                        "severity": "warning"
                    })

        # Verificar que no haya placeholders sin resolver
        placeholders = ["[COMPLETAR]", "[TODO]", "[VERIFICAR]",
                        "<<PENDIENTE>>"]
        for ph in placeholders:
            if ph in document:
                issues.append({
                    "section": "global",
                    "type": "unresolved_placeholder",
                    "detail": f"Placeholder '{ph}' encontrado",
                    "severity": "blocker"
                })

        # Verificar consistencia de datos numéricos
        issues.extend(self._check_numeric_consistency(document))

        # Verificar términos prohibidos
        voice = self.template["voice"]
        for term in voice.get("prohibited_terms", []):
            if term.lower() in document.lower():
                issues.append({
                    "section": "global",
                    "type": "prohibited_term",
                    "detail": f"Término prohibido: '{term}'",
                    "severity": "warning"
                })

        self.automated_checks = issues
        return issues

    def get_review_requirements(self) -> list[dict]:
        """Lista secciones que requieren revisión humana."""
        requirements = []
        for section in self.template["sections"]:
            if section.get("requires_human_review", False):
                requirements.append({
                    "section": section["id"],
                    "status": self.reviews.get(
                        section["id"], ReviewStatus.PENDING
                    ),
                    "reviewer_required": "senior",
                })
        return requirements

    def is_deliverable_ready(self) -> tuple[bool, list[str]]:
        """Verifica si el documento puede entregarse."""
        blockers = []

        # Verificar checks automáticos
        for issue in self.automated_checks:
            if issue["severity"] == "blocker":
                blockers.append(
                    f"Blocker: {issue['detail']} "
                    f"en {issue['section']}"
                )

        # Verificar revisiones humanas
        for section in self.template["sections"]:
            if section.get("requires_human_review"):
                status = self.reviews.get(section["id"])
                if status != ReviewStatus.APPROVED:
                    blockers.append(
                        f"Revisión pendiente: {section['id']} "
                        f"({status or 'no revisado'})"
                    )

        return (len(blockers) == 0, blockers)
