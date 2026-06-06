# Extraído de: LibroAIGateway/cap-18-keys-cifrado-master.md
# Revisión post-break-glass (gateway/app/api/v1/admin/break_glass.py)
async def review(event_id: int, body: ReviewRequest, user: dict):
    if event.admin1_id == user_id or event.admin2_id == user_id:
        raise HTTPException(403, "reviewer no puede ser firmante")
    event.reviewed_by = user_id
    event.review_decision = body.decision  # legitimate | flagged | escalated
