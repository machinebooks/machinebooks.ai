# Extracted from: LibroAIGateway/cap-21-audit-append-only.md
async def verify_chain(db, from_id, to_id) -> dict:
    # ...loads rows in order...
    for row in rows:
        expected = compute_chain_hash(_row_to_dict(row), prev_hash)
        if row.chain_hash != expected:
            return {"valid": False, "broken_at_id": row.id,
                    "message": "Hash mismatch: tampering detected"}
        prev_hash = row.chain_hash
    return {"valid": True, "verified": verified, "message": "Chain intact"}
