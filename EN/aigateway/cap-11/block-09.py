# Extracted from: LibroAIGateway/cap-11-tools-code-web-documents.md
ALLOWED_EXTENSIONS = {
    ".pdf", ".docx", ".pptx", ".xlsx", ".xls",
    ".txt", ".md", ".csv", ".jsonl", ".html", ".htm",
}
MAX_FILE_BYTES = 50 * 1024 * 1024  # 50 MB

def validate_document(filename: str, data: bytes) -> str:
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(415, f"Unsupported extension: {ext}")
    if len(data) > MAX_FILE_BYTES:        # cap by bytes, not by characters
        raise HTTPException(413, "File too large (max 50 MB)")
    return ext
