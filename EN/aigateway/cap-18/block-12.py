# Extracted from: LibroAIGateway/cap-18-keys-encryption-master.md
# Post-break-glass review (gateway/app/api/v1/admin/break_glass.py)
async def review(event_id: int, body: ReviewRequest, user: dict):
    if event.admin1_id == user_id or event.admin2_id == user_id:
        raise HTTPException(403, "reviewer cannot be a signer")
    event.reviewed_by = user_id
    event.review_decision = body.decision  # legitimate | flagged | escalated
