# Extracted from: LibroAIGateway/cap-10-embeddings-images-audio.md
# gateway/app/api/v1/audio.py:299-304
content_type = _CONTENT_TYPE_MAP.get(body.response_format, "audio/mpeg")
return StreamingResponse(
    iter([azure_resp.content]),
    media_type=content_type,
    headers={"Content-Disposition": f"inline; filename=speech.{body.response_format}"},
)
