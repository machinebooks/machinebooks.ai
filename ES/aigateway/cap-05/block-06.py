# Extraído de: LibroAIGateway/cap-05-router-smart-select.md
@staticmethod
def _matches_condition(condition: dict, context: dict) -> bool:
    """AND lógico: todas las claves de la condición deben coincidir."""
    for key, value in (condition or {}).items():
        ctx_value = context.get(key)
        if ctx_value is None:
            return False
        if isinstance(value, list):
            if ctx_value not in value:
                return False
        elif str(ctx_value).lower() != str(value).lower():
            return False
    return True
