# Extraído de: LibroAIGateway/cap-30-portal-usuario.md
# gateway/app/api/v1/spending.py — gasto personal
@router.get("/me")
async def my_spending(request, db):
    user_id = await _resolve_user_id(request)
    row = await db.execute(text("""
        SELECT COALESCE(SUM(cost_usd), 0) AS total_cost,
               COALESCE(SUM(CASE WHEN created_at >= :today THEN cost_usd END), 0) AS today,
               -- week, month, year...
        FROM audit_logs
        WHERE employee_id = :uid  # ← Estricto. Sin fallback a device_id.
    """), {"uid": user_id})
    # by_model, by_purpose, by_client...
