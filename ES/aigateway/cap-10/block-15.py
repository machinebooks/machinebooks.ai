# Extraído de: LibroAIGateway/cap-10-embeddings-imagenes-audio.md
# gateway/app/api/v1/images.py:293-307 (sintetizado)
image_bytes = await image.read()
if len(image_bytes) > _MAX_IMAGE_BYTES:  # 4 MB
    raise HTTPException(413, "imagen demasiado grande")

# Magic-bytes: rechazar si extensión no coincide con contenido real
img_ext = (image.filename or "").rsplit(".", 1)[-1].lower()
if img_ext not in {"png", "jpg", "jpeg", "webp", "gif"}:
    raise HTTPException(415, "Formato de imagen no soportado")
ok, info = validate_file_type(image_bytes, img_ext)
if not ok:
    raise HTTPException(415, "Tipo de imagen no coincide con extensión")
