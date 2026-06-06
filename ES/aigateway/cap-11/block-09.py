# Extraído de: LibroAIGateway/cap-11-tools-codigo-web-documentos.md
ALLOWED_EXTENSIONS = {
    ".pdf", ".docx", ".pptx", ".xlsx", ".xls",
    ".txt", ".md", ".csv", ".jsonl", ".html", ".htm",
}
MAX_FILE_BYTES = 50 * 1024 * 1024  # 50 MB

def validate_document(filename: str, data: bytes) -> str:
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(415, f"Extensión no soportada: {ext}")
    if len(data) > MAX_FILE_BYTES:        # cap por bytes, no por caracteres
        raise HTTPException(413, "Fichero demasiado grande (máx. 50 MB)")
    return ext
