# Extraído de: LibroTecnico/cap-14-agentes-orchestrator.md
def read_file(path: str, section: str = "") -> str:
    """Lee cualquier fichero y devuelve contenido estructurado."""
    if not os.path.exists(path):
        return f"Error: fichero no encontrado: {path}"

    ext = os.path.splitext(path)[1].lower()

    if ext in ('.docx',):
        return _read_docx(path, section)     # Texto + headings + tablas
    elif ext in ('.xlsx', '.xlsm', '.xls'):
        return _read_excel(path)             # Hojas + primeras filas
    elif ext == '.pdf':
        return _read_pdf(path)               # Texto extraído con PyMuPDF
    else:
        # Ficheros de texto: truncar a 50K caracteres
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        if len(content) > 50000:
            content = content[:50000] + "\n\n[...truncado a 50K chars...]"
        return content
