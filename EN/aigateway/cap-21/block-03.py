# Extracted from: LibroAIGateway/cap-21-audit-append-only.md
def compute_chain_hash(row_data: dict, prev_hash: str) -> str:
    payload = (
        f"{prev_hash}|{row_data['id']}|{row_data['request_id']}"
        f"|{row_data['device_id']}|{row_data['prompt_hash']}"
        f"|{row_data['created_at']}"
    )
    return hash_sha256(payload)
