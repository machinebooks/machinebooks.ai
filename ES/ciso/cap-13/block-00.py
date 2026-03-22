# Extraído de: LibroCISO/cap-13-orquestador-copiloto.md
# Ejemplo didáctico: patrones/ai/copilot_orchestrator.py

from enum import Enum
from dataclasses import dataclass, field
from typing import AsyncGenerator
import time
import uuid

class CopilotMode(str, Enum):
    """Tres modos de ejecución del copiloto."""
    CHAT_RAG = "chat_rag"           # Respuesta directa con contexto normativo
    AGENT_TOOLS = "agent_tools"     # Un agente con herramientas
    ORCHESTRATE = "orchestrate"     # Multi-agente coordinado

@dataclass
class CopilotRequest:
    """Entrada del usuario ya validada por guardrails."""
    message: str
    session_id: str
    user_id: str
    module_context: str             # Módulo GRC activo (privacy, risk, compliance...)
    tenant_id: str                  # Multi-tenancy obligatorio
    mode_override: CopilotMode | None = None  # El usuario puede forzar un modo

@dataclass
class OrchestratorStep:
    """Un paso individual dentro de una ejecución orquestada."""
    step_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    agent_name: str = ""
    action: str = ""
    input_summary: str = ""
    output_summary: str = ""
    tokens_used: int = 0
    cost_eur: float = 0.0
    duration_ms: int = 0
    status: str = "pending"         # pending | running | completed | failed

class CopilotOrchestrator:
    """
    Orquestador central del copiloto IA.
    Clasifica intención, aplica guardrails y delega a uno de tres modos.
    """

    def __init__(self, llm_factory, rag_service, agent_registry, guardrails):
        self.llm_factory = llm_factory          # Factoría multi-proveedor (Cap. 10)
        self.rag_service = rag_service          # Servicio RAG normativo (Cap. 11)
        self.agent_registry = agent_registry    # Registro de agentes (Cap. 12)
        self.guardrails = guardrails            # Pipeline de guardrails
        self.intent_classifier = IntentClassifier()

    async def process(
        self, request: CopilotRequest
    ) -> AsyncGenerator[dict, None]:
        """
        Punto de entrada principal. Devuelve un generador asíncrono
        de eventos SSE para streaming al frontend.
        """
        execution_id = str(uuid.uuid4())
        start_time = time.monotonic()

        # 1. Guardrails de entrada (bloquean si detectan riesgo)
        guard_result = await self.guardrails.scan(request.message)
        if not guard_result.passed:
            yield {
                "type": "error",
                "code": guard_result.violation_code,
                "message": guard_result.user_message
            }
            # Registrar en audit_trail incluso las solicitudes bloqueadas
            await self._log_blocked_request(request, guard_result, execution_id)
            return

        # 2. Clasificar intención → modo de ejecución
        mode = request.mode_override or self.intent_classifier.classify(
            message=request.message,
            module_context=request.module_context
        )

        yield {"type": "mode_selected", "mode": mode.value}

        # 3. Delegar al modo correspondiente
        if mode == CopilotMode.CHAT_RAG:
            async for event in self._execute_chat_rag(request, execution_id):
                yield event

        elif mode == CopilotMode.AGENT_TOOLS:
            async for event in self._execute_agent(request, execution_id):
                yield event

        elif mode == CopilotMode.ORCHESTRATE:
            async for event in self._execute_orchestration(request, execution_id):
                yield event

        # 4. Registrar ejecución completa en audit_trail
        elapsed_ms = int((time.monotonic() - start_time) * 1000)
        yield {"type": "completed", "execution_id": execution_id, "duration_ms": elapsed_ms}
