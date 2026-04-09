# Extraido de: LibroAISafety/cap-22-arquitectura-segura.md
from typing import Any
from dataclasses import dataclass, field

@dataclass
class ToolPermission:
    """Define los permisos de una herramienta para un contexto dado."""
    tool_name: str
    allowed_actions: list[str]
    max_calls_per_session: int = 10
    requires_user_confirmation: bool = False
    allowed_parameters: dict[str, Any] = field(default_factory=dict)

# Ejemplo: perfil de permisos para un agente de consulta de costes
COST_AGENT_PERMISSIONS = [
    ToolPermission(
        tool_name="query_database",
        allowed_actions=["SELECT"],    # solo lectura, nunca UPDATE/DELETE
        max_calls_per_session=20,
        allowed_parameters={"tables": ["costs", "budgets", "usage"]},
    ),
    ToolPermission(
        tool_name="send_alert",
        allowed_actions=["email"],
        max_calls_per_session=3,       # máximo 3 alertas por sesión
        requires_user_confirmation=True,  # requiere aprobación humana
    ),
    ToolPermission(
        tool_name="modify_budget",
        allowed_actions=[],            # deshabilitado — solo lectura
        max_calls_per_session=0,
    ),
]

def validate_tool_call(
    tool_name: str,
    action: str,
    params: dict,
    permissions: list[ToolPermission],
    session_calls: dict[str, int],
) -> bool:
    """
    Valida que una llamada a herramienta cumple los permisos definidos.
    Retorna False si la llamada debe ser bloqueada.
    """
    perm = next((p for p in permissions if p.tool_name == tool_name), None)
    if perm is None:
        return False  # herramienta no autorizada

    if action not in perm.allowed_actions:
        return False  # acción no permitida

    calls = session_calls.get(tool_name, 0)
    if calls >= perm.max_calls_per_session:
        return False  # límite de llamadas superado

    # Validar parámetros si hay restricciones definidas
    for key, allowed_values in perm.allowed_parameters.items():
        if key in params and params[key] not in allowed_values:
            return False  # parámetro fuera de rango permitido

    return True
