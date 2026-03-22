# Extraído de: LibroTecnico/cap-26-desarrollador-futuro.md
def pipeline_validacion_codigo(
    codigo_generado: str,
    requisitos_negocio: str
) -> dict:
    """
    Pipeline de validación multi-perspectiva para código generado por IA.
    El arquitecto supervisa el resultado; el pipeline ejecuta la revisión sistemática.
    Usar claude-opus-4-6 en la síntesis garantiza razonamiento de alta calidad
    para la decisión final sobre si el código puede pasar a producción.
    """
    # Paso 1: revisión de seguridad independiente
    revision_seguridad = revisor_seguridad(
        tarea=f"Revisa este código:\n\n