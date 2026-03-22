# Extraído de: LibroCISO/cap-27-executive-dashboard.md
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph

async def export_executive_pdf(
    dashboard_data: dict,
    organization_name: str,
    period: str,
) -> bytes:
    """Genera PDF ejecutivo para distribución al comité.

    Estructura:
    1. Cabecera: organización, periodo, fecha de generación
    2. GRC Score con semáforo
    3. KPIs destacados en tabla
    4. Desglose por módulo
    5. Compliance frameworks
    6. Disclaimer: datos a fecha de generación
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    # Cabecera
    elements.append(Paragraph(
        f"Informe Ejecutivo GRC — {organization_name}",
        style_title
    ))
    elements.append(Paragraph(
        f"Periodo: {period} | Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
        style_subtitle
    ))

    # GRC Score
    score = dashboard_data.get("overall_grc_score")
    color = "verde" if score and score >= 80 else \
            "ámbar" if score and score >= 60 else "rojo"
    elements.append(Paragraph(
        f"Score GRC Global: {score} ({color})",
        style_score
    ))

    # ... módulos, frameworks, disclaimer ...

    doc.build(elements)
    return buffer.getvalue()
