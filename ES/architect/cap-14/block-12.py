# Extraído de: LibroTecnico/cap-14-agentes-orchestrator.md
# Ejemplo didáctico: patrones/tools/tool_validation.py

from pydantic import BaseModel, Field, field_validator

class SearchOpportunitiesInput(BaseModel):
    """Schema de validación para la herramienta search_opportunities."""
    keywords: str = Field(..., min_length=2, max_length=200)
    budget_min: float | None = Field(None, ge=0, le=1_000_000_000)
    category: str | None = None
    max_results: int = Field(default=10, ge=1, le=50)

    @field_validator("category")
    @classmethod
    def validate_category(cls, v):
        if v and v.lower() not in VALID_CATEGORIES:
            raise ValueError(
                f"Categoría '{v}' no válida. "
                f"Opciones: {', '.join(VALID_CATEGORIES)}"
            )
        return v.lower() if v else v

def execute_tool(name: str, raw_params: dict) -> dict:
    """Ejecuta una herramienta con validación previa de parámetros."""
    schema = TOOL_SCHEMAS.get(name)
    if not schema:
        return {"error": f"Herramienta '{name}' no registrada"}

    try:
        validated = schema(**raw_params)
    except ValidationError as e:
        # Devolver error descriptivo para que el agente corrija
        return {"error": f"Parámetros inválidos: {e.errors()}"}

    return TOOL_EXECUTORS[name](validated)
