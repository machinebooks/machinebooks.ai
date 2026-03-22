# Extraído de: LibroBugBounty/cap-18-report-bounty.md
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def generate_report_pdf(report_data, output_path):
    """Genera un PDF profesional para el reporte."""
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # Header
    story.append(Paragraph(
        f"Security Vulnerability Report — {report_data['target']}",
        styles['Title']
    ))
    story.append(Paragraph(
        f"Reporter: {report_data['reporter']}<br/>"
        f"Date: {report_data['date']}<br/>"
        f"Classification: CONFIDENTIAL — Vendor Disclosure",
        styles['Normal']
    ))
    story.append(Spacer(1, 20))

    # Sections
    for section in report_data['sections']:
        story.append(Paragraph(section['title'], styles['Heading2']))
        story.append(Paragraph(section['content'], styles['Normal']))
        story.append(Spacer(1, 12))

    doc.build(story)
