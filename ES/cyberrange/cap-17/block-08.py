# Extraído de: LibroCyberrange/cap-17-generacion-escenarios-ia.md
# Ejemplo didáctico: cyber-range-builder/backend/routers/ai_scenarios.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from backend.auth import get_current_user, role_required
from backend.services.ai.scenario_generator import ScenarioGeneratorService

router = APIRouter(prefix="/ai/scenarios", tags=["AI Scenarios"])
generator = ScenarioGeneratorService()

class GenerateScenarioRequest(BaseModel):
    description: str
    workzone_id: int
    complexity: Optional[str] = "standard"  # "standard" o "complex"

class GenerateScenarioResponse(BaseModel):
    success: bool
    template_id: Optional[int] = None
    scenario: Optional[dict] = None
    errors: Optional[list] = None
    message: str

@router.post("/generate", response_model=GenerateScenarioResponse)
async def generate_scenario(
    request: GenerateScenarioRequest,
    current_user = Depends(role_required(["admin", "organizer"])),
):
    """
    Genera un escenario completo a partir de una descripción
    en lenguaje natural. Solo disponible para administradores
    y organizadores.

    El escenario generado se almacena como template privado
    y requiere revisión humana antes de publicarse.
    """
    if len(request.description) < 20:
        raise HTTPException(
            status_code=400,
            detail="La descripción debe tener al menos 20 caracteres"
        )

    if len(request.description) > 5000:
        raise HTTPException(
            status_code=400,
            detail="La descripción no puede exceder 5000 caracteres"
        )

    result = await generator.generate_scenario(
        description=request.description,
        workzone_id=request.workzone_id,
        author_id=current_user.id,
        complexity=request.complexity,
    )

    return GenerateScenarioResponse(**result)


@router.post("/generate/{template_id}/deploy")
async def deploy_generated_scenario(
    template_id: int,
    background_tasks: BackgroundTasks,
    current_user = Depends(role_required(["admin", "organizer"])),
):
    """
    Despliega un escenario previamente generado y revisado.
    La ejecución es asíncrona vía Celery.
    """
    # Verificar que el template existe y pertenece al usuario
    db = next(get_db())
    template = db.query(ScenarioTemplate).filter(
        ScenarioTemplate.id == template_id,
        ScenarioTemplate.author_id == current_user.id
    ).first()

    if not template:
        raise HTTPException(status_code=404, detail="Template no encontrado")

    # Encolar tarea de despliegue
    from backend.tasks.deployment import deploy_scenario_task
    task = deploy_scenario_task.delay(
        template_id=template_id,
        user_id=current_user.id
    )

    return {
        "message": "Despliegue iniciado",
        "task_id": task.id,
        "template_id": template_id
    }
