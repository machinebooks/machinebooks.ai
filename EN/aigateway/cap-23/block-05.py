# Extracted from: LibroAIGateway/cap-23-compliance-regulatory.md
# gateway/app/api/v1/admin/compliance.py:189-206
@router.put("/content-categories/{cat_id}")
async def update_content_category(...):
    cat = result.scalar_one_or_none()
    if not cat:
        raise HTTPException(404, detail="Category not found")
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(cat, field, value)
    await db.commit()
    ContentClassifierService.invalidate_cache()  # ← immediate propagation
