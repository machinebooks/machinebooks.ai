# Extraído de: LibroCISO/cap-21-celery-async.md
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/reports", tags=["reports"])


class ReportRequest(BaseModel):
    framework_ids: list[int]
    format: str = "pdf"  # pdf, docx, xlsx
    include_ai_summary: bool = False


class ReportResponse(BaseModel):
    report_id: int
    task_id: str
    status: str
    poll_url: str


class TaskStatusResponse(BaseModel):
    report_id: int
    task_id: str
    status: str  # pending, running, completed, failed, timeout
    progress: int  # 0-100
    phase: str | None = None  # Descripción de la fase actual
    file_url: str | None = None  # URL de descarga si completado
    error: str | None = None


@router.post("/", response_model=ReportResponse,
             status_code=status.HTTP_202_ACCEPTED)
async def create_report(
    request: ReportRequest,
    current_user=Depends(get_current_user),
    session=Depends(get_session),
):
    """
    Solicita la generación de un informe de cumplimiento.
    Devuelve 202 Accepted con task_id para polling de estado.
    """
    # Crear registro en BD
    report = Report(
        tenant_id=current_user.tenant_id,
        requested_by=current_user.id,
        framework_ids=request.framework_ids,
        format=request.format,
        status=ReportStatus.PENDING,
    )
    session.add(report)
    session.commit()

    # Encolar tarea asíncrona
    task = generate_compliance_report.apply_async(
        kwargs={
            "report_id": report.id,
            "tenant_id": current_user.tenant_id,
            "framework_ids": request.framework_ids,
            "format": request.format,
            "include_ai_summary": request.include_ai_summary,
        },
        # Cola ya definida en el decorador, pero se puede sobreescribir
    )

    # Guardar task_id en el registro para correlación
    report.celery_task_id = task.id
    session.commit()

    return ReportResponse(
        report_id=report.id,
        task_id=task.id,
        status="pending",
        poll_url=f"/api/v1/reports/{report.id}/status",
    )


@router.get("/{report_id}/status", response_model=TaskStatusResponse)
async def get_report_status(
    report_id: int,
    current_user=Depends(get_current_user),
    session=Depends(get_session),
):
    """
    Consulta el estado de un informe en generación.
    El frontend llama a este endpoint cada 3-5 segundos.
    """
    report = session.get(Report, report_id)
    if not report or report.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Informe no encontrado")

    # Consultar estado en Celery para obtener progreso en tiempo real
    result = generate_compliance_report.AsyncResult(report.celery_task_id)

    progress = 0
    phase = None
    if result.state == "PROGRESS":
        progress = result.info.get("progress", 0)
        phase = result.info.get("phase")
    elif result.state == "SUCCESS":
        progress = 100

    return TaskStatusResponse(
        report_id=report.id,
        task_id=report.celery_task_id,
        status=report.status.value,
        progress=progress,
        phase=phase,
        file_url=(
            f"/api/v1/reports/{report.id}/download"
            if report.status == ReportStatus.COMPLETED else None
        ),
        error=report.error_message,
    )
