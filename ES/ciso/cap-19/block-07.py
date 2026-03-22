# Extraído de: LibroCISO/cap-19-dashboards-copiloto.md
# Ejemplo didáctico: endpoint del copiloto con inyección de contexto
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/ai/copilot", tags=["copilot"])

@router.post("/chat")
async def copilot_chat(
    request: CopilotChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    corporate_id: int = Depends(get_tenant),
):
    """
    Endpoint de chat del copiloto con streaming SSE.
    Inyecta el contexto del módulo y registro activo en el prompt.
    """
    # 1. Recuperar contexto de la entidad si existe
    entity_context = ""
    if request.context.entity_id:
        entity_context = await _load_entity_context(
            db, corporate_id,
            request.context.module,
            request.context.entity_type,
            request.context.entity_id,
        )

    # 2. Construir el system prompt con contexto de módulo
    #    Este prompt es lo que diferencia un copiloto de un chatbot genérico
    system_prompt = _build_copilot_system_prompt(
        module=request.context.module,
        entity_context=entity_context,
        user_role=current_user.role,
    )

    # 3. Streaming con generador asíncrono
    async def event_stream():
        # Evento de progreso mientras se prepara
        yield f"data: {json.dumps({'type': 'progress', 'message': 'Preparando contexto...'})}\n\n"

        # Llamar al LLM con streaming
        async for chunk in llm_factory.stream(
            model_service="copilot",
            system=system_prompt,
            messages=request.history + [{"role": "user", "content": request.message}],
            max_tokens=2048,
            user_id=current_user.id,
            corporate_id=corporate_id,
        ):
            if chunk.type == "text":
                yield f"data: {json.dumps({'type': 'token', 'content': chunk.text})}\n\n"
            elif chunk.type == "tool_use":
                yield f"data: {json.dumps({'type': 'progress', 'message': f'Ejecutando: {chunk.tool_name}...'})}\n\n"

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # Desactivar buffering de Nginx
        },
    )


async def _load_entity_context(
    db: AsyncSession, corporate_id: int,
    module: str, entity_type: str, entity_id: int,
) -> str:
    """
    Carga el contexto de la entidad que el usuario está viendo.
    Devuelve un texto estructurado que se inyecta en el system prompt.
    """
    if module == "privacy" and entity_type == "treatment":
        treatment = await db.get(Treatment, entity_id)
        if treatment and treatment.corporate_id == corporate_id:
            return (
                f"El usuario está viendo el tratamiento: {treatment.name}\n"
                f"Base jurídica: {treatment.legal_basis}\n"
                f"Categorías de datos: {', '.join(treatment.data_categories)}\n"
                f"Estado DPIA: {treatment.dpia_status}\n"
                f"Interesados aproximados: {treatment.estimated_subjects}\n"
                f"Última revisión: {treatment.last_review}\n"
            )
    elif module == "risk" and entity_type == "risk":
        risk = await db.get(Risk, entity_id)
        if risk and risk.corporate_id == corporate_id:
            return (
                f"El usuario está viendo el riesgo: {risk.name}\n"
                f"Nivel inherente: {risk.inherent_level}\n"
                f"Nivel residual: {risk.residual_level}\n"
                f"Controles asociados: {len(risk.controls)}\n"
            )
    # ... más módulos
    return ""


def _build_copilot_system_prompt(
    module: str, entity_context: str, user_role: str,
) -> str:
    """
    Construye el system prompt del copiloto inyectando contexto de módulo,
    entidad activa y rol del usuario. Esta función es la pieza clave que
    convierte un chatbot genérico en un copiloto contextual.
    """
    # Base: identidad, alcance y restricciones del copiloto
    base = (
        "Eres el copiloto GRC de la Plataforma. Tu función es asistir "
        "a profesionales de cumplimiento regulatorio (DPOs, CISOs, "
        "auditores, analistas de riesgos) en sus tareas diarias.\n\n"
        "REGLAS FUNDAMENTALES:\n"
        "- Responde SOLO sobre el dominio regulatorio del módulo activo.\n"
        "- Cita siempre el artículo o norma que sustenta tu respuesta.\n"
        "- Si no tienes certeza suficiente, dilo explícitamente.\n"
        "- NUNCA generes datos inventados: si no dispones de información "
        "del registro actual, indícalo.\n"
        "- Tus respuestas son orientativas — NO constituyen asesoramiento "
        "legal y requieren validación profesional.\n"
        "- NO ejecutes acciones destructivas (eliminar, notificar a "
        "autoridades) sin confirmación explícita del usuario.\n"
    )

    # Contexto de módulo: qué normativa aplica
    module_contexts = {
        "privacy": (
            "Módulo activo: PRIVACIDAD.\n"
            "Normativa principal: RGPD (Reglamento UE 2016/679) y "
            "LOPDGDD (Ley Orgánica 3/2018).\n"
            "Puedes asistir con: registro de tratamientos (Art. 30), "
            "evaluaciones de impacto (Art. 35), derechos ARCO+ "
            "(Arts. 15-22), notificación de brechas (Art. 33-34), "
            "legitimación y bases jurídicas (Art. 6).\n"
        ),
        "risk": (
            "Módulo activo: RIESGO.\n"
            "Metodologías soportadas: MAGERIT, FAIR, NIST RMF, "
            "OCTAVE, EBIOS RM, ISO 27005.\n"
            "Puedes asistir con: identificación de activos, catálogos "
            "de amenazas, valoración de riesgos, planes de tratamiento "
            "y nivel de riesgo residual.\n"
        ),
        "compliance": (
            "Módulo activo: CUMPLIMIENTO.\n"
            "Marcos soportados: ENS (RD 311/2022), ISO 27001:2022, "
            "NIS2, DORA, ISO 27701, SOC 2.\n"
            "Puedes asistir con: evaluación de controles, gap analysis, "
            "Declaración de Aplicabilidad, evidencias y niveles de "
            "madurez.\n"
        ),
        # ... más módulos con su contexto normativo específico
    }

    # Contexto de rol: qué nivel de detalle esperar
    role_hints = {
        "dpo": "El usuario es un DPO. Prioriza privacidad y datos personales.",
        "ciso": "El usuario es un CISO. Prioriza visión ejecutiva y riesgo.",
        "auditor": "El usuario es un auditor. Prioriza evidencias y trazabilidad.",
        "analyst": "El usuario es un analista. Prioriza detalle técnico.",
    }

    prompt = base
    prompt += module_contexts.get(module, f"Módulo activo: {module}.\n")
    prompt += role_hints.get(user_role, "") + "\n"

    # Contexto de la entidad concreta que el usuario está viendo
    if entity_context:
        prompt += (
            "\nCONTEXTO DEL REGISTRO ACTUAL (inyectado automáticamente):\n"
            f"{entity_context}\n"
            "Usa esta información para dar respuestas específicas al "
            "registro, no genéricas.\n"
        )

    return prompt
