# Extracted from: LibroAIGateway/cap-11-tools-code-web-documents.md
async def extract_document(
    request: Request, file: UploadFile, cache_key: str,
) -> ExtractResult:
    data = await file.read()
    ext = validate_document(file.filename, data)
    sha256 = hash_sha256(data)
    started = time.monotonic()

    text, extractor = _convert_with_markitdown(data, ext)  # main engine
    if text is None:
        text, extractor = _convert_fallback(data, ext)     # backup engine

    return ExtractResult(
        text=text,
        format=ext.lstrip("."),
        chars=len(text),
        sha256=sha256,
        processing_ms=int((time.monotonic() - started) * 1000),
        extractor=extractor,
    )
