# Extraído de: LibroConsultor/cap-14-reporting.md
def priorizar_recomendaciones(
    hallazgos: list[Hallazgo],
    presupuesto_cliente: str,
    restricciones: str,
    voice_prompt: str
) -> str:
    """Genera la sección de recomendaciones priorizadas."""

    hallazgos_texto = "\n\n".join(
        f"ID: {h.id}\n"
        f"Recomendación: {h.recomendacion}\n"
        f"Severidad: {h.severidad.value}\n"
        f"Prioridad sugerida: {h.prioridad.value}\n"
        f"Esfuerzo: {h.esfuerzo_estimado}\n"
        f"Coste estimado: {h.coste_estimado or 'No estimado'}\n"
        f"Impacto: {h.impacto_negocio}"
        for h in hallazgos
    )

    prompt = f"""Genera la sección de recomendaciones priorizadas
para un informe de consultoría.

RECOMENDACIONES INDIVIDUALES:
{hallazgos_texto}

PRESUPUESTO DISPONIBLE DEL CLIENTE: {presupuesto_cliente}
RESTRICCIONES: {restricciones}

INSTRUCCIONES:
1. Agrupa en tres bloques: Inmediatas (0-30 días),
   Corto plazo (1-3 meses), Medio plazo (3-12 meses).
2. Dentro de cada bloque, ordena por relación impacto/esfuerzo.
3. Para cada recomendación: acción + plazo + responsable sugerido
   + coste estimado + impacto esperado.
4. Marca dependencias entre recomendaciones.
5. Identifica "quick wins": alto impacto, bajo esfuerzo.
6. Si el presupuesto no cubre todo, indica qué descartar y por qué.
7. Formato: tabla Markdown para el resumen, prosa para la narrativa."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=voice_prompt,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text
