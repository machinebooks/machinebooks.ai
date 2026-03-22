# Extraído de: LibroCyberrange/cap-09-fastapi-escala.md
# backend/routers/admin_workzones.py
router = APIRouter(
    prefix="/admin/workzones",
    tags=["Admin"],
    dependencies=[Depends(role_required("admin"))]  # Protege TODOS los endpoints
)
