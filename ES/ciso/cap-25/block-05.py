# Extraído de: LibroCISO/cap-25-vigilancia-normativa.md
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class CreateSourceRequest(BaseModel):
    name: str
    source_type: str = "official_journal"
    url: str | None = None
    country: str | None = None
    check_frequency: str = "daily"
    is_active: bool = True


@router.get("/dashboard")
async def get_dashboard(user: CurrentUser, db: DbSession):
    """Dashboard agregado de vigilancia normativa."""
    svc = RegulatoryWatchService(db, user["corporate_id"])
    return {"data": await svc.get_dashboard()}


@router.get("/updates")
async def list_updates(
    user: CurrentUser, db: DbSession,
    status: str | None = None,
    sector: str | None = None,
    skip: int = 0, limit: int = 50,
):
    """Lista actualizaciones con filtros y paginación."""
    svc = RegulatoryWatchService(db, user["corporate_id"])
    items, total = await svc.list_updates(
        status=status, sector=sector,
        skip=skip, limit=limit
    )
    return {"data": items, "total": total}


@router.post("/updates/{update_id}/analyze-impact")
async def analyze_impact(
    update_id: int, user: CurrentUser, db: DbSession
):
    """Dispara análisis de impacto con IA sobre una actualización."""
    svc = RegulatoryWatchService(db, user["corporate_id"])
    result = await svc.analyze_impact(update_id)
    if result is None:
        raise HTTPException(404, "Actualización no encontrada")
    await db.commit()
    return {"data": result}


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: int, user: CurrentUser, db: DbSession
):
    """Confirma lectura de una alerta normativa."""
    svc = RegulatoryWatchService(db, user["corporate_id"])
    result = await svc.acknowledge_alert(alert_id, user["user_id"])
    if result is None:
        raise HTTPException(404, "Alerta no encontrada")
    await db.commit()
    return {"data": result}
