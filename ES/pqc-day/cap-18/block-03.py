# Extraído de: LibroPQC/cap-18-roadmap.md
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph,
    Spacer, PageBreak, KeepTogether
)
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from datetime import datetime
from typing import Dict, Any, List
import os


class TechnicalReportGenerator:
    """
    Genera informe técnico detallado con ReportLab.

    Incluye: portada, resumen ejecutivo en tabla,
    hallazgos agrupados por severidad con fichero y línea,
    distribución de algoritmos, y plan de acción priorizado.
    """

    SEVERITY_COLORS = {
        'critical': colors.HexColor('#d32f2f'),
        'high': colors.HexColor('#f57c00'),
        'medium': colors.HexColor('#fbc02d'),
        'low': colors.HexColor('#388e3c'),
    }

    def __init__(self, output_dir: str = '/tmp'):
        self.output_dir = output_dir
        self.styles = getSampleStyleSheet()
        self._add_custom_styles()

    def _add_custom_styles(self):
        """Estilos personalizados para el informe PQC"""
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=22,
            textColor=colors.HexColor('#1565c0'),
            spaceAfter=24,
            alignment=TA_CENTER,
        ))
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#37474f'),
            spaceBefore=16,
            spaceAfter=8,
        ))

    def generate(
        self,
        analysis_data: Dict[str, Any],
        findings: List[Dict],
        actions: List[Dict],
        risk_scenarios: List[Dict]
    ) -> str:
        """Genera el informe técnico completo"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"pqc_technical_{timestamp}.pdf"
        path = os.path.join(self.output_dir, filename)

        doc = SimpleDocTemplate(path, pagesize=A4,
                                leftMargin=2*cm, rightMargin=2*cm,
                                topMargin=2.5*cm, bottomMargin=2*cm)

        story = []
        story.extend(self._cover_page(analysis_data))
        story.extend(self._executive_summary(analysis_data))
        story.extend(self._findings_by_severity(findings))
        story.extend(self._algorithm_distribution(analysis_data))
        story.extend(self._action_plan(actions))
        story.extend(self._risk_summary(risk_scenarios))

        doc.build(story)
        return path

    def _cover_page(self, data: Dict) -> List:
        """Portada con KPIs principales"""
        story = [Spacer(1, 3 * cm)]
        story.append(Paragraph(
            "Informe de Análisis<br/>Criptográfico Post-Cuántico",
            self.styles['ReportTitle']
        ))
        story.append(Spacer(1, 1 * cm))

        # Tabla de KPIs
        kpi_data = [
            ['Hallazgos totales', str(data.get('total_findings', 0))],
            ['Quantum-vulnerables', str(data.get('quantum_vulnerable', 0))],
            ['Score PQC', f"{data.get('pqc_score', 0):.1f}/100"],
            ['Acciones pendientes', str(data.get('pending_actions', 0))],
        ]
        kpi_table = Table(kpi_data, colWidths=[8*cm, 5*cm])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#e3f2fd')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1565c0')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 13),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#90caf9')),
        ]))
        story.append(kpi_table)
        story.append(PageBreak())
        return story

    def _findings_by_severity(self, findings: List[Dict]) -> List:
        """Tabla de hallazgos agrupados por severidad"""
        story = []
        story.append(Paragraph(
            "Hallazgos criptográficos", self.styles['SectionHeader']
        ))

        # Cabecera de tabla
        header = ['Algoritmo', 'Fichero', 'Severidad', 'PQC', 'Migración']
        rows = [header]

        for f in sorted(findings, key=lambda x: (
            {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
            .get(x.get('severity', 'low'), 4)
        )):
            rows.append([
                f.get('algorithm', 'N/A'),
                f.get('file_path', 'N/A')[:40],  # Truncar path largo
                f.get('severity', 'N/A').upper(),
                'No' if f.get('quantum_vulnerable') else 'Sí',
                f.get('pqc_recommendation', 'Pendiente')[:25]
            ])

        table = Table(rows, colWidths=[3*cm, 6*cm, 2*cm, 1.5*cm, 4*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1565c0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1),
             [colors.white, colors.HexColor('#f5f5f5')]),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        story.append(table)
        story.append(PageBreak())
        return story

    def _action_plan(self, actions: List[Dict]) -> List:
        """Plan de acción priorizado con plazos"""
        story = []
        story.append(Paragraph(
            "Plan de acción priorizado", self.styles['SectionHeader']
        ))

        header = ['Acción', 'Prioridad', 'Plazo', 'Esfuerzo', 'Estado']
        rows = [header]

        for action in actions:
            rows.append([
                action.get('title', 'N/A')[:45],
                action.get('priority', 'N/A').upper(),
                str(action.get('due_date', 'N/A')),
                action.get('estimated_effort', 'N/A'),
                action.get('status', 'pending').upper()
            ])

        table = Table(rows, colWidths=[6*cm, 2*cm, 2.5*cm, 3*cm, 2.5*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#37474f')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1),
             [colors.white, colors.HexColor('#fafafa')]),
        ]))
        story.append(table)
        return story

    # _executive_summary, _algorithm_distribution y _risk_summary
    # siguen el mismo patrón: datos → tabla o gráfico → story
