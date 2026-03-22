# Extraído de: LibroCISO/cap-27-executive-dashboard.md
from fastapi import APIRouter
from api.deps import CurrentUser, DbSession

router = APIRouter()


@router.get("/dashboard")
async def get_executive_dashboard(
    user: CurrentUser, db: DbSession
):
    """Dashboard ejecutivo GRC — vista consolidada
    para el comité de dirección.

    Requiere rol: ciso, admin, executive_viewer
    """
    from services.executive_dashboard_service import (
        ExecutiveDashboardService
    )
    svc = ExecutiveDashboardService(db, user["corporate_id"])
    return {"data": await svc.get_dashboard()}
