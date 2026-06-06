# Extracted from: LibroAIGateway/cap-30-user-portal.md
# gateway/app/api/v1/me.py — password change
@router.post("/change-password")
async def change_password(body: ChangePasswordRequest, request, db):
    uid = await _user_id(request)
    _validate_password_strength(body.new_password)  # min 10, upper+lower+digit+sym
    user = await _current_user(request, db)
    if not verify_password(body.current_password, user.password_hash):
        raise HTTPException(401, "The current password is not correct")
    user.password_hash = hash_password(body.new_password)
    await db.commit()
    # 1. After change: invalidate ALL sessions
    await SessionService.revoke_user(await get_redis(), user.id)
    return {"data": {"ok": True}}
