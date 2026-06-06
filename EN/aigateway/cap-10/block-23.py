# Extracted from: LibroAIGateway/cap-10-embeddings-images-audio.md
# gateway/app/api/v1/audio.py:396-400 (synthesized)
estimated_tokens = max(1, len(file_bytes) // 1000)  # input ~1 token/KB
transcript_text = response_payload.get("text") or ""
transcript_tok = max(0, len(transcript_text) // 4)  # output ~1 token/4 chars
