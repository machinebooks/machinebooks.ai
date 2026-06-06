# Extracted from: LibroAIGateway/cap-09-compression-tokens.md
# gateway/app/services/prompt_compression_service.py:36-51 (synthesized)
# Isolate code blocks so they are not compressed
code_blocks: list[str] = []
def stash(match: re.Match) -> str:
    code_blocks.append(match.group(0))
    return f"\x00CODE{len(code_blocks)-1}\x00"

stashed = re.sub(r"`[\s\S]*?`", stash, text)

# Rules on text outside code
stashed = _RE_MULTI_SPACE.sub(" ", stashed)
stashed = _RE_TRAILING_WS.sub("\n", stashed)
stashed = _RE_MULTI_NEWLINE.sub("\n\n", stashed)
stashed = _RE_HR_SEPARATOR.sub(lambda m: m.group(1) * 10, stashed)

# Restore code intact
for idx, block in enumerate(code_blocks):
    stashed = stashed.replace(f"\x00CODE{idx}\x00", block)
