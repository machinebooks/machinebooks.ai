# Extraído de: LibroCISO/cap-19-dashboards-copiloto.md
# Ejemplo didáctico: endpoint de listado con paginación servidor
@router.get("/treatments")
async def list_treatments(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),  # Máximo 100 filas por página
    sort_by: str = Query("last_review"),
    sort_order: str = Query("desc"),
    legal_basis: str | None = Query(None),
    dpia_status: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    corporate_id: int = Depends(get_tenant),
):
    query = select(Treatment).where(Treatment.corporate_id == corporate_id)

    # Filtros opcionales
    if legal_basis:
        query = query.where(Treatment.legal_basis == legal_basis)
    if dpia_status:
        query = query.where(Treatment.dpia_status == dpia_status)

    # Contar total antes de paginar (para total_pages)
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    # Ordenar y paginar
    sort_column = getattr(Treatment, sort_by, Treatment.last_review)
    order = desc(sort_column) if sort_order == "desc" else asc(sort_column)
    query = query.order_by(order).offset((page - 1) * page_size).limit(page_size)

    items = (await db.execute(query)).scalars().all()
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=ceil(total / page_size),
    )
