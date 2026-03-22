# Extraído de: LibroPQC/cap-18-roadmap.md
from typing import Dict, Any, List


class RoadmapOrchestrator:
    """
    Coordina el flujo completo de generación del roadmap:
    1. Priorizar hallazgos con el framework Europol
    2. Generar acciones de remediación agrupadas
    3. Crear escenarios de riesgo para hallazgos críticos
    4. Generar informes PDF para las tres audiencias
    """

    def __init__(self, priority_calculator, action_manager,
                 risk_evaluator, report_generators):
        self.priority = priority_calculator
        self.actions = action_manager
        self.risk = risk_evaluator
        self.reports = report_generators

    def generate_roadmap(
        self,
        assessment_id: int,
        findings: List[dict],
        organization_name: str,
        db_session
    ) -> Dict[str, Any]:
        """
        Ejecuta el pipeline completo de roadmap.

        Retorna rutas a los tres PDFs generados
        y estadísticas del proceso.
        """
        # Paso 1: Priorizar todos los hallazgos
        prioritized = self.priority.prioritize_findings(findings)

        # Paso 2: Generar acciones agrupadas
        actions = self.actions.generate_actions_from_findings(
            assessment_id, prioritized, db_session
        )

        # Paso 3: Crear escenarios de riesgo para hallazgos
        #         con score >= 25 (high/critical)
        risk_scenarios = []
        for finding in prioritized:
            if finding.get('priority_score', 0) >= 25:
                scenario = self.risk.evaluate_risk_scenario(
                    asset_name=finding.get('service', 'Sistema'),
                    asset_type='software',
                    threat_description=(
                        f"Adversario con capacidad cuántica explota "
                        f"{finding.get('algorithm', 'algoritmo vulnerable')}"
                    ),
                    vulnerability_description=(
                        f"Uso de {finding.get('algorithm', 'N/A')} "
                        f"en {finding.get('file_path', 'N/A')}"
                    ),
                    inherent_likelihood=min(
                        finding.get('exposure', 3), 5
                    ),
                    inherent_impact=min(
                        finding.get('severity_score', 3), 5
                    ),
                    controls_applied=finding.get('controls', [])
                )
                risk_scenarios.append(scenario)

        # Paso 4: Agregar datos para informes
        report_data = self._compile_report_data(
            organization_name, prioritized, actions, risk_scenarios
        )

        # Paso 5: Generar los tres PDF
        technical_pdf = self.reports['technical'].generate(
            report_data, prioritized, actions, risk_scenarios
        )
        executive_pdf = self.reports['executive'](
            report_data
        )
        # El compliance_pdf sigue la misma plantilla
        # WeasyPrint con controles mapeados a frameworks

        return {
            'technical_report': technical_pdf,
            'executive_report': executive_pdf,
            'statistics': {
                'findings_analyzed': len(findings),
                'actions_generated': len(actions),
                'risk_scenarios_created': len(risk_scenarios),
                'critical_actions': sum(
                    1 for a in actions if a['priority'] == 'critical'
                ),
                'high_actions': sum(
                    1 for a in actions if a['priority'] == 'high'
                ),
                'average_risk_reduction': (
                    sum(s['risk_reduction_percentage']
                        for s in risk_scenarios) / len(risk_scenarios)
                    if risk_scenarios else 0
                )
            }
        }

    def _compile_report_data(
        self, org_name, findings, actions, scenarios
    ) -> Dict[str, Any]:
        """Compila datos agregados para las plantillas de informes"""
        return {
            'organization': org_name,
            'total_findings': len(findings),
            'quantum_vulnerable': sum(
                1 for f in findings
                if f.get('quantum_vulnerable', True)
            ),
            'pqc_score': self._calculate_pqc_score(findings),
            'pending_actions': sum(
                1 for a in actions if a['status'] == 'pending'
            ),
            'risk_reduction': round(
                sum(s['risk_reduction_percentage'] for s in scenarios)
                / max(len(scenarios), 1), 1
            ),
            'risk_distribution': {
                'critical': sum(
                    1 for f in findings
                    if f.get('priority_label') == 'critical'
                ),
                'high': sum(
                    1 for f in findings
                    if f.get('priority_label') == 'high'
                ),
                'medium': sum(
                    1 for f in findings
                    if f.get('priority_label') == 'medium'
                ),
                'low': sum(
                    1 for f in findings
                    if f.get('priority_label') == 'low'
                ),
            },
            'top_actions': actions[:5]
        }

    def _calculate_pqc_score(self, findings: List[dict]) -> float:
        """
        Score de preparación PQC: porcentaje de hallazgos
        que ya son PQC-compliant o tienen migración completada.
        """
        if not findings:
            return 100.0
        compliant = sum(
            1 for f in findings
            if not f.get('quantum_vulnerable', True)
        )
        return round(compliant / len(findings) * 100, 1)
