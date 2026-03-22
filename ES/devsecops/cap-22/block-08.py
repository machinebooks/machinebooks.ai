# Extraído de: LibroDevSecOps/cap-22-compliance-continuo.md
from datetime import datetime


class ComplianceReportGenerator:
    """Genera informes legibles para auditores."""

    def generate_audit_report(
        self,
        assessments: list[ControlAssessment],
        framework: str,
        report_date: datetime,
    ) -> str:
        """Genera un informe Markdown para el auditor."""

        compliant = [
            a for a in assessments
            if a.status == ComplianceStatus.COMPLIANT
        ]
        non_compliant = [
            a for a in assessments
            if a.status == ComplianceStatus.NON_COMPLIANT
        ]
        partial = [
            a for a in assessments
            if a.status == ComplianceStatus.PARTIAL
        ]
        not_assessed = [
            a for a in assessments
            if a.status == ComplianceStatus.NOT_ASSESSED
        ]

        total = len(assessments)
        pct = (len(compliant) / total * 100) if total > 0 else 0

        report = f"""# Informe de Compliance — {framework}

**Fecha:** {report_date.strftime('%Y-%m-%d %H:%M UTC')}
**Evaluador:** Pipeline DevSecOps automatizado
**Periodo de evidencia:** Últimos 30 días

## Resumen ejecutivo

| Estado | Controles | Porcentaje |
|--------|-----------|------------|
| Cumplido | {len(compliant)} | {pct:.1f}% |
| No cumplido | {len(non_compliant)} | {len(non_compliant)/total*100:.1f}% |
| Parcial | {len(partial)} | {len(partial)/total*100:.1f}% |
| No evaluado | {len(not_assessed)} | {len(not_assessed)/total*100:.1f}% |
| **Total** | **{total}** | **100%** |

## Controles no cumplidos (requieren acción)

"""
        for a in non_compliant:
            report += f"""### {a.control.control_id} — {a.control.title}

- **Estado:** No cumplido
- **Causa:** {a.justification}
- **Evidencias evaluadas:** {len(a.evidences)}
- **Próxima revisión:** {a.next_review.strftime('%Y-%m-%d') if a.next_review else 'N/A'}

"""

        report += "## Controles cumplidos (con evidencia)\n\n"
        for a in compliant:
            evidence_list = ", ".join(
                f"{e.source.value} ({e.timestamp.strftime('%Y-%m-%d')})"
                for e in a.evidences
            )
            report += (
                f"- **{a.control.control_id}** — {a.control.title}: "
                f"{evidence_list}\n"
            )

        return report
