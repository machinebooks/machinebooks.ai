# Extraído de: LibroConsultor/cap-09-generacion-propuestas.md
def construir_system_prompt_con_voz(
    tipo: SeccionTipo,
    referencias_estilo: list[str]
) -> str:
    """Añade ejemplos de voz de la práctica al system prompt base."""
    base = SYSTEM_PROMPTS[tipo]

    # Extraer primeros 2 párrafos de cada referencia como ejemplo de tono
    ejemplos_tono = []
    for ref in referencias_estilo[:2]:
        parrafos = ref.split("\n\n")[:2]
        ejemplos_tono.append("\n\n".join(parrafos))

    adicion = f"""

EJEMPLOS DE TONO Y ESTILO DE LA FIRMA (adapta el tono, NO copies el contenido):

Ejemplo 1:
{ejemplos_tono[0] if ejemplos_tono else '(no disponible)'}

Ejemplo 2:
{ejemplos_tono[1] if len(ejemplos_tono) > 1 else '(no disponible)'}

Mantén este nivel de formalidad, estructura de frases y vocabulario técnico."""

    return base + adicion
