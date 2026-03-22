# Extraído de: LibroPQC/cap-16-dora.md
"""
Generador de informes DORA-PQC para auditores.
Produce PDFs estructurados con scoring, hallazgos y recomendaciones.
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime

class DoraReportGenerator:
    """Genera informes DORA-PQC en formato PDF profesional."""

    def __init__(self, assessment: dict, entity: dict):
        self.assessment = assessment
        self.entity = entity
        self.styles = getSampleStyleSheet()
        self._configure_styles()

    def _configure_styles(self):
        """Estilos corporativos para informes regulatorios."""
        self.styles.add(ParagraphStyle(
            "ReportTitle",
            parent=self.styles["Heading1"],
            fontSize=18,
            spaceAfter=20,
        ))
        self.styles.add(ParagraphStyle(
            "SectionHeader",
            parent=self.styles["Heading2"],
            fontSize=14,
            spaceBefore=15,
            spaceAfter=10,
        ))

    def generate(self, output_path: str):
        """Genera el informe PDF completo."""
        doc = SimpleDocTemplate(
            output_path, pagesize=A4,
            leftMargin=2.5*cm, rightMargin=2.5*cm,
            topMargin=2*cm, bottomMargin=2*cm,
        )

        elements = []
        elements.extend(self._build_cover())
        elements.append(PageBreak())
        elements.extend(self._build_executive_summary())
        elements.append(PageBreak())
        elements.extend(self._build_scoring_section())
        elements.extend(self._build_findings_section())
        elements.extend(self._build_regulatory_timeline())
        elements.extend(self._build_recommendations())

        doc.build(elements)

    def _build_scoring_section(self) -> list:
        """Sección de scoring multidimensional."""
        elements = []
        score = self.assessment["score"]

        elements.append(Paragraph(
            "Scoring de Preparación PQC bajo DORA",
            self.styles["SectionHeader"],
        ))

        # Tabla de scores por dimensión
        data = [
            ["Dimensión", "Score", "Riesgo", "Referencia DORA"],
            [
                "Vida útil del dato",
                f"{score['shelf_life_score']}/100",
                self._risk_label(score["shelf_life_score"]),
                "Art. 6 (gestión riesgos TIC)",
            ],
            [
                "Exposición HNDL",
                f"{score['exposure_score']}/100",
                self._risk_label(score["exposure_score"]),
                "Art. 9 (protección/prevención)",
            ],
            [
                "Severidad de impacto",
                f"{score['severity_score']}/100",
                self._risk_label(score["severity_score"]),
                "Art. 11 (continuidad)",
            ],
            [
                "Complejidad migración",
                f"{score['migration_score']}/100",
                self._risk_label(score["migration_score"]),
                "Art. 26 (pruebas resiliencia)",
            ],
            [
                "SCORE GLOBAL",
                f"{score['overall_score']}/100",
                score["risk_category"].upper(),
                "Reglamento (UE) 2022/2554",
            ],
        ]

        table = Table(data, colWidths=[5*cm, 3*cm, 3*cm, 5*cm])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a237e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#e8eaf6")),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 15))

        # Días hasta deadline G7
        days = score["g7_deadline_days"]
        urgency = "CRÍTICO" if days < 365 else "ALTO" if days < 730 else "PLANIFICABLE"
        elements.append(Paragraph(
            f"Días hasta deadline G7 CEG (2030-2032): <b>{days}</b> — "
            f"Nivel de urgencia: <b>{urgency}</b>",
            self.styles["Normal"],
        ))

        return elements

    def _build_regulatory_timeline(self) -> list:
        """Línea temporal regulatoria con hitos PQC."""
        elements = []
        elements.append(Paragraph(
            "Línea Temporal Regulatoria",
            self.styles["SectionHeader"],
        ))

        milestones = [
            ["Fecha", "Hito", "Regulador", "Impacto"],
            ["Ene 2025", "DORA en vigor", "UE", "Obligatorio"],
            ["Dic 2026", "Inventario criptográfico", "CE", "Obligatorio"],
            ["2027", "CNSA 2.0 en adquisiciones", "NSA", "Federal EE.UU."],
            ["2028", "Identificación dependencias", "NCSC UK", "Obligatorio"],
            ["2030", "Deprecación RSA/ECC", "NIST", "Federal EE.UU."],
            ["2030-2032", "Sistemas críticos migrados", "G7 CEG", "Recomendado"],
            ["2035", "Prohibición RSA/ECC", "NIST/CNSA", "Obligatorio"],
        ]

        table = Table(milestones, colWidths=[3*cm, 5*cm, 3*cm, 3*cm])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a237e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ]))

        elements.append(table)
        return elements

    @staticmethod
    def _risk_label(score: float) -> str:
        if score >= 75:
            return "CRÍTICO"
        elif score >= 50:
            return "ALTO"
        elif score >= 25:
            return "MEDIO"
        return "BAJO"
