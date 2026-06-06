# Extraído de: LibroAIGateway/cap-30-portal-usuario.md
# gateway/app/api/v1/me.py — compliance disclosures
@router.get("/compliance")
async def get_my_compliance(request, db):
    uid = await _user_id(request)
    required = await governance.get_required_acks(db)
    accepted = await governance.get_user_acks(db, uid)
    pending = [k for k, v in required.items()
               if accepted.get(k, 0) < v]
    return {"data": {"required": required, "accepted": accepted, "pending": pending}}
