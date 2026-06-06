# Extracted from: LibroAIGateway/cap-21-audit-append-only.md
if prev_hash.startswith("chain_gap_"):
    return {
        "valid": False,
        "broken_at_id": rows[0].id,
        "message": "Chain gap detected: previous row not contiguous",
    }
