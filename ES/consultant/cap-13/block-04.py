# Extraído de: LibroConsultor/cap-13-gap-analysis.md
class MultiFrameworkAnalyzer:
    """Analiza gaps cruzando múltiples frameworks."""

    def __init__(self, agent: GapAnalysisAgent):
        self.agent = agent
        self.unified_gaps: list[GapFinding] = []

    def run_unified_analysis(
        self, evidence_processor: EvidenceProcessor
    ) -> list[GapFinding]:
        """Ejecuta gap analysis multi-framework deduplicado."""
        raw_findings: list[GapFinding] = []

        # Fase 1: evaluar cada control de cada framework
        for fw_name, controls in self.agent.frameworks.items():
            for control in controls:
                evidence = evidence_processor \
                    .get_evidence_for_control(control.control_id)
                finding = self.agent.evaluate_control(
                    control, evidence
                )
                raw_findings.append(finding)

        # Fase 2: agrupar por equivalencia cruzada
        groups = self._group_by_cross_reference(raw_findings)

        # Fase 3: unificar cada grupo en un solo gap
        for group in groups:
            unified = self._unify_group(group)
            self.unified_gaps.append(unified)

        return self.unified_gaps

    def _group_by_cross_reference(
        self, findings: list[GapFinding]
    ) -> list[list[GapFinding]]:
        """Agrupa findings que refieren al mismo gap real."""
        # Union-Find para agrupar controles equivalentes
        parent: dict[str, str] = {}

        def find(x: str) -> str:
            while parent.get(x, x) != x:
                x = parent[x]
            return x

        def union(a: str, b: str) -> None:
            parent[find(a)] = find(b)

        # Construir grupos basados en cross_references
        for finding in findings:
            ctrl = finding.control
            key = f"{ctrl.framework}:{ctrl.control_id}"
            for ref in ctrl.cross_references:
                union(key, ref)

        # Agrupar findings por raíz
        groups_map: dict[str, list[GapFinding]] = {}
        for finding in findings:
            ctrl = finding.control
            key = f"{ctrl.framework}:{ctrl.control_id}"
            root = find(key)
            groups_map.setdefault(root, []).append(finding)

        return list(groups_map.values())

    def _unify_group(
        self, group: list[GapFinding]
    ) -> GapFinding:
        """Unifica un grupo de findings equivalentes."""
        # Tomar el nivel más bajo como conservador
        worst_level = min(f.current_level for f in group)
        # Tomar el esfuerzo máximo (no sumar)
        max_effort = max(f.effort_days for f in group)
        # Recopilar todos los frameworks afectados
        all_frameworks = list({
            f.control.framework for f in group
        })

        primary = group[0]  # El primero como base
        return GapFinding(
            control=primary.control,
            current_level=MaturityLevel(worst_level),
            target_level=self.agent.target_level,
            evidence_summary=primary.evidence_summary,
            gap_description=primary.gap_description,
            remediation=primary.remediation,
            effort_days=max_effort,
            priority=primary.priority,
            confidence=min(f.confidence for f in group),
            affected_frameworks=all_frameworks,
        )
