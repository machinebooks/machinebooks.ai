# Extraído de: LibroConsultor/cap-09-generacion-propuestas.md
SYSTEM_PROMPTS = {
    SeccionTipo.COMPRENSION_NECESIDAD: """Eres un consultor senior redactando
la sección de comprensión de la necesidad para una propuesta técnica.

REGLAS:
- Demuestra que entiendes el problema ESPECÍFICO del cliente, no el problema genérico.
- Referencia datos concretos del pliego: plazos, volúmenes, restricciones.
- Identifica riesgos que el cliente no ha mencionado explícitamente.
- Usa lenguaje directo y técnico. Sin adjetivos vacíos.
- Extensión: 800-1.200 palabras.
- Estructura: contexto → problema → implicaciones → nuestra lectura.
- NO uses frases genéricas como "entendemos su necesidad" o "somos conscientes de la importancia".
- CADA párrafo debe contener al menos un dato específico del pliego o del cliente.""",

    SeccionTipo.ENFOQUE_TECNICO: """Eres un arquitecto de IA redactando
la sección de enfoque técnico para una propuesta de consultoría.

REGLAS:
- Describe el enfoque con precisión técnica: herramientas, metodologías, estándares.
- Conecta cada decisión técnica con un beneficio para el cliente.
- Incluye alternativas consideradas y razón del descarte (demuestra criterio).
- Detalla entregables específicos por fase, no genéricos.
- Extensión: 1.500-2.500 palabras.
- Estructura: enfoque global → fases con actividades → entregables → herramientas.
- NO uses lenguaje de marketing. El evaluador es técnico.""",

    SeccionTipo.RESUMEN_EJECUTIVO: """Eres un director de consultoría redactando
el resumen ejecutivo de una propuesta técnica.

REGLAS:
- Máximo 2 páginas (600-800 palabras).
- Primera frase: por qué el cliente debería elegirnos (dato o diferencial concreto).
- Condensa: comprensión, enfoque, equipo, diferencial, compromiso.
- Tono: confianza basada en datos, no en adjetivos.
- Este resumen se escribe DESPUÉS de todas las demás secciones.
- NUNCA empieces con "Tenemos el placer de presentar" ni variantes."""
}

def generar_seccion(
    tipo: SeccionTipo,
    contexto: ContextoPropuesta,
    secciones_referencia: list[dict],
    secciones_previas: dict[SeccionTipo, str] | None = None
) -> SeccionGenerada:
    """Genera una sección de la propuesta con contexto RAG."""

    # Construir el contexto para el prompt
    refs_texto = "\n\n---\n\n".join([
        f"[Referencia {i+1} — {ref['sector']}, {ref['tipo_servicio']}, "
        f"puntuación: {ref['puntuacion']}]\n{ref['contenido']}"
        for i, ref in enumerate(secciones_referencia[:3])
    ])

    requisitos_texto = "\n".join([
        f"- {r['descripcion']} (obligatorio: {r.get('obligatorio', True)})"
        for r in contexto.requisitos_pliego[:20]
    ])

    criterios_texto = "\n".join([
        f"- {c['nombre']}: {c['puntuacion_maxima']} puntos — {c.get('descripcion', '')}"
        for c in contexto.criterios_valoracion
    ])

    # Contexto de secciones ya generadas (coherencia narrativa)
    previas_texto = ""
    if secciones_previas:
        previas_texto = "\n\nSECCIONES YA REDACTADAS (mantén coherencia):\n"
        for tipo_prev, contenido_prev in secciones_previas.items():
            # Solo primeros 500 chars como resumen
            previas_texto += f"\n[{tipo_prev.value}]: {contenido_prev[:500]}...\n"

    user_prompt = f"""Genera la sección de {tipo.value} para esta propuesta.

CLIENTE: {contexto.cliente} — Sector: {contexto.sector}
TIPO DE SERVICIO: {contexto.tipo_servicio}
FECHA LÍMITE: {contexto.fecha_entrega.strftime('%d/%m/%Y')}

REQUISITOS DEL PLIEGO:
{requisitos_texto}

CRITERIOS DE VALORACIÓN:
{criterios_texto}

RESTRICCIONES:
{chr(10).join(f'- {r}' for r in contexto.restricciones)}

SECCIONES DE REFERENCIA (propuestas ganadoras anteriores):
{refs_texto}
{previas_texto}

Genera la sección siguiendo las reglas del system prompt.
Prioriza la especificidad sobre la generalidad."""

    response = client_anthropic.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=SYSTEM_PROMPTS[tipo],
        messages=[{"role": "user", "content": user_prompt}]
    )

    contenido = response.content[0].text
    tokens_total = response.usage.input_tokens + response.usage.output_tokens
    # Coste aproximado de claude-sonnet-4-6
    coste = (response.usage.input_tokens * 3.0 +
             response.usage.output_tokens * 15.0) / 1_000_000

    return SeccionGenerada(
        tipo=tipo,
        contenido=contenido,
        tokens_consumidos=tokens_total,
        coste_generacion=coste
    )
