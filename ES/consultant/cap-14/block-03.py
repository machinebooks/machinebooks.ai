# Extraído de: LibroConsultor/cap-14-reporting.md
def generar_resumen_ejecutivo(
    proyecto: ProyectoReporting,
    secciones_generadas: dict[str, str],
    voice_prompt: str
) -> str:
    """Genera el resumen ejecutivo a partir del informe completo."""

    # Agrupar hallazgos por severidad para el resumen
    hallazgos_por_severidad = {}
    for h in proyecto.hallazgos:
        sev = h.severidad.value
        hallazgos_por_severidad.setdefault(sev, []).append(h)

    resumen_hallazgos = "\n".join(
        f"- {sev}: {len(lista)} hallazgos"
        for sev, lista in hallazgos_por_severidad.items()
    )

    # Top 5 recomendaciones por impacto
    top_recomendaciones = sorted(
        proyecto.hallazgos,
        key=lambda h: list(Severidad).index(h.severidad)
    )[:5]

    top_recs_texto = "\n".join(
        f"- [{h.prioridad.value}] {h.recomendacion}"
        for h in top_recomendaciones
    )

    prompt_ejecutivo = f"""Redacta el resumen ejecutivo de este informe de consultoría.

PROYECTO: {proyecto.nombre_proyecto}
TIPO: {proyecto.tipo}
CLIENTE: {proyecto.cliente}
PERIODO: {proyecto.fecha_inicio} a {proyecto.fecha_fin}
ALCANCE: {proyecto.alcance}

DISTRIBUCIÓN DE HALLAZGOS:
{resumen_hallazgos}

TOP 5 RECOMENDACIONES POR IMPACTO:
{top_recs_texto}

SECCIÓN DE ANÁLISIS YA REDACTADA:
{secciones_generadas.get('analisis', 'No disponible')}

INSTRUCCIONES:
1. Máximo 500 palabras (2 páginas con formato).
2. Primer párrafo: qué se hizo y qué se encontró (3 frases).
3. Segundo párrafo: los 3-5 hallazgos más relevantes con impacto.
4. Tercer párrafo: las recomendaciones prioritarias con plazos.
5. Párrafo final: próximos pasos inmediatos (qué debe decidir
   el cliente esta semana).
6. Lenguaje de negocio, no técnico. Un CFO debe entenderlo.
7. Cada recomendación con dato de impacto si existe."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=voice_prompt,
        messages=[{"role": "user", "content": prompt_ejecutivo}]
    )
    return response.content[0].text
