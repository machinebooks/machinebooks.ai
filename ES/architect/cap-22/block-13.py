# Extraído de: LibroTecnico/cap-22-observabilidad.md
# Disclaimer IA obligatorio en todos los informes PDF
_ai_disclaimer_style = ParagraphStyle(
    'AIDisclaimer', parent=styles['Body'],
    fontName='Helvetica-Oblique', fontSize=8.5, leading=12,
    textColor=colors.HexColor('#6B7280'),
    backColor=colors.HexColor('#FFF8E1'),       # Fondo ámbar claro
    borderWidth=0.5, borderColor=colors.HexColor('#F59E0B'),
    borderPadding=8, spaceBefore=8*mm, spaceAfter=4*mm,
)

elements.append(Paragraph(
    "<b>AVISO IMPORTANTE — Contenido generado por Inteligencia Artificial:</b> "
    "Este informe ha sido generado de forma automatizada mediante modelos de "
    "IA a partir de los datos disponibles en el sistema. "
    "Las cifras, análisis, recomendaciones y conclusiones deben ser revisadas "
    "y validadas por los responsables del área antes de tomar decisiones.",
    _ai_disclaimer_style,
))
