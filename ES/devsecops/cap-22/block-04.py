# Extraído de: LibroDevSecOps/cap-22-compliance-continuo.md
from datetime import datetime, timezone, timedelta


class ComplianceEvaluator:
    """Evalúa el estado de cumplimiento de cada control."""

    # Evidencia caduca pasados 30 días sin nueva ejecución
    MAX_EVIDENCE_AGE = timedelta(days=30)

    def __init__(self, mappings: list[dict], evidences: list[Evidence]):
        self.mappings = mappings
        self.evidences = evidences

    def evaluate_all(self) -> list[ControlAssessment]:
        """Evalúa todos los controles del framework."""
        assessments = []
        now = datetime.now(timezone.utc)

        for mapping in self.mappings:
            control = Control(
                framework=mapping["framework"],
                control_id=mapping["control_id"],
                title=mapping["title"],
                category=mapping.get("category", "technical"),
                automation_level=mapping.get("automation_level", "full"),
            )

            # Buscar evidencias relevantes para este control
            required_sources = [
                s["type"] for s in mapping.get("evidence_sources", [])
            ]
            relevant = self._find_relevant_evidences(required_sources)

            # Evaluar estado
            status, justification = self._assess_control(
                control, required_sources, relevant, now
            )

            assessments.append(ControlAssessment(
                control=control,
                status=status,
                evidences=relevant,
                assessed_at=now,
                assessed_by="pipeline:compliance-evaluator",
                justification=justification,
                next_review=now + self.MAX_EVIDENCE_AGE,
            ))

        return assessments

    def _assess_control(
        self,
        control: Control,
        required_sources: list[str],
        evidences: list[Evidence],
        now: datetime,
    ) -> tuple[ComplianceStatus, str]:
        """Determina si un control se cumple."""

        if not required_sources:
            return (
                ComplianceStatus.NOT_ASSESSED,
                "Control sin fuentes de evidencia automatizadas",
            )

        # Verificar que hay evidencia de cada fuente requerida
        found_sources = {e.source.value for e in evidences}
        missing = set(required_sources) - found_sources
        if missing:
            return (
                ComplianceStatus.NON_COMPLIANT,
                f"Faltan evidencias de: {', '.join(missing)}",
            )

        # Verificar que las evidencias no están caducadas
        stale = [
            e for e in evidences
            if (now - e.timestamp) > self.MAX_EVIDENCE_AGE
        ]
        if stale:
            sources_stale = [e.source.value for e in stale]
            return (
                ComplianceStatus.PARTIAL,
                f"Evidencias caducadas (>30 días): "
                f"{', '.join(sources_stale)}",
            )

        # Verificar que todas las evidencias pasaron
        failed = [e for e in evidences if not e.passed]
        if failed:
            sources_failed = [e.source.value for e in failed]
            return (
                ComplianceStatus.NON_COMPLIANT,
                f"Checks fallidos: {', '.join(sources_failed)}",
            )

        return (
            ComplianceStatus.COMPLIANT,
            "Todas las evidencias presentes, vigentes y exitosas",
        )

    def _find_relevant_evidences(
        self, required_sources: list[str]
    ) -> list[Evidence]:
        """Encuentra las evidencias más recientes de cada fuente."""
        latest: dict[str, Evidence] = {}
        for evidence in self.evidences:
            source = evidence.source.value
            if source in required_sources:
                existing = latest.get(source)
                if not existing or evidence.timestamp > existing.timestamp:
                    latest[source] = evidence
        return list(latest.values())
