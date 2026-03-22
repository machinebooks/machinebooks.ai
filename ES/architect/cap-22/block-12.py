# Extraído de: LibroTecnico/cap-22-observabilidad.md
# Constantes de marcado AI — EU AI Act Art. 50.2
_GENERATOR = "la Plataforma – IA Generativa"
_CATEGORY = "AI-Generated"
_KEYWORDS = "AI-generated, EU-AI-Act-Art50, machine-generated-content"
_COMMENT = (
    "Documento generado total o parcialmente mediante Inteligencia Artificial. "
    "Revise y valide el contenido antes de su uso."
)

def stamp_docx(doc) -> None:
    """Marca un documento Word con metadatos AI-generated y disclaimer visible."""
    # 1. Metadatos invisibles (propiedades del archivo)
    cp = doc.core_properties
    cp.comments = _COMMENT
    cp.keywords = _KEYWORDS
    cp.category = _CATEGORY
    cp.content_status = "AI-Generated – Pendiente de revisión"
    if not cp.author:
        cp.author = _GENERATOR
    else:
        cp.author = f"{cp.author} | {_GENERATOR}"

    # 2. Disclaimer visible en el footer de todas las secciones
    _FOOTER_TEXT = (
        "Documento generado con asistencia de IA — "
        "Revise y valide el contenido antes de su uso"
    )
    for section in doc.sections:
        footer = section.footer
        footer.is_linked_to_previous = False
        existing = "".join(p.text for p in footer.paragraphs).strip()
        if _FOOTER_TEXT in existing:
            continue  # No duplicar si ya existe
        para = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = para.add_run(_FOOTER_TEXT)
        run.font.size = Pt(7)
        run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)
        run.font.italic = True
