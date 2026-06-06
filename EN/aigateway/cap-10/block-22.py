# Extracted from: LibroAIGateway/cap-10-embeddings-images-audio.md
# gateway/app/api/v1/audio.py:347-357 (synthesized)
if len(file_bytes) > _MAX_AUDIO_BYTES:  # 25 MB
    raise HTTPException(413, "file too large (max 25 MB)")
if audio_ext not in {"wav", "mp3", "m4a", "ogg", "flac", "webm", "mp4"}:
    raise HTTPException(415, "Audio format not supported")
ok, info = validate_file_type(file_bytes, audio_ext)
if not ok:
    raise HTTPException(415, "Audio type does not match extension")
