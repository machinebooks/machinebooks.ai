# Extracted from: LibroAIGateway/cap-10-embeddings-images-audio.md
# gateway/app/api/v1/images.py:293-307 (synthesized)
image_bytes = await image.read()
if len(image_bytes) > _MAX_IMAGE_BYTES:  # 4 MB
    raise HTTPException(413, "image too large")

# Magic-bytes: reject if extension doesn't match actual content
img_ext = (image.filename or "").rsplit(".", 1)[-1].lower()
if img_ext not in {"png", "jpg", "jpeg", "webp", "gif"}:
    raise HTTPException(415, "Image format not supported")
ok, info = validate_file_type(image_bytes, img_ext)
if not ok:
    raise HTTPException(415, "Image type does not match extension")
