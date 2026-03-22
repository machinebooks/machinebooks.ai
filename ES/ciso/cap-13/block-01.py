# Extraído de: LibroCISO/cap-13-orquestador-copiloto.md
# Ejemplo didáctico: patrones/ai/intent_classifier.py

import re
from typing import Optional

# Patrones que indican tareas de agente (verbos de acción + dominio)
AGENT_PATTERNS = [
    (r"\b(genera|prepara|crea|redacta|elabora)\b.*\b(informe|reporte|documento)\b", "report_writer"),
    (r"\b(analiza|evalúa|revisa)\b.*\b(riesgo|amenaza|vulnerabilidad)\b", "risk"),
    (r"\b(analiza|evalúa|revisa)\b.*\b(tratamiento|datos personales|privacidad)\b", "privacy"),
    (r"\b(verifica|comprueba|audita)\b.*\b(cumplimiento|control|marco|ENS|ISO)\b", "compliance"),
    (r"\b(importa|carga|procesa)\b.*\b(documento|fichero|CSV|Excel)\b", "data_import"),
]

# Patrones que indican orquestación multi-agente
ORCHESTRATION_PATTERNS = [
    r"\b(DPIA|evaluación de impacto)\b",    # DPIA = privacy + risk + compliance + report
    r"\b(análisis completo|informe integral|evaluación global)\b",
    r"\b(plan de tratamiento)\b.*\b(riesgo)\b",  # Plan = risk + compliance + report
    r"\b(auditoría|gap analysis)\b.*\b(completa|integral)\b",
]

# Herramientas detectables por nombre explícito
TOOL_KEYWORDS = {
    "PrivacyAgent": "privacy",
    "RiskAgent": "risk",
    "ComplianceAgent": "compliance",
    "ReportWriter": "report_writer",
}

class IntentClassifier:
    """
    Clasificador híbrido: heurísticas primero, LLM como fallback.
    """

    def classify(
        self, message: str, module_context: str
    ) -> CopilotMode:
        msg_lower = message.lower().strip()

        # Paso 1: ¿Es claramente una orquestación multi-agente?
        for pattern in ORCHESTRATION_PATTERNS:
            if re.search(pattern, msg_lower):
                return CopilotMode.ORCHESTRATE

        # Paso 2: ¿Es una tarea para un agente específico?
        for pattern, agent_key in AGENT_PATTERNS:
            if re.search(pattern, msg_lower):
                return CopilotMode.AGENT_TOOLS

        # Paso 3: ¿Es una pregunta informativa? (sin verbos de acción)
        if msg_lower.startswith(("qué", "cuál", "cómo", "por qué", "dónde",
                                  "cuándo", "explica", "describe", "define")):
            return CopilotMode.CHAT_RAG

        # Paso 4: Fallback → CHAT_RAG (el modo más seguro y barato)
        # En producción, aquí iría la llamada a claude-haiku-4-5
        # como fallback de clasificación para mensajes ambiguos
        return CopilotMode.CHAT_RAG

    async def classify_with_llm_fallback(
        self, message: str, module_context: str, llm_factory
    ) -> CopilotMode:
        """Fallback con LLM para mensajes que las heurísticas no resuelven."""
        # Solo se invoca cuando classify() no tiene confianza suficiente
        response = await llm_factory.create_completion(
            service_name="intent_classification",
            model_preference="claude-haiku-4-5",  # Modelo rápido y barato
            messages=[{
                "role": "user",
                "content": f"""Clasifica esta solicitud del usuario en uno de tres modos:
- CHAT_RAG: pregunta informativa que se responde con búsqueda documental
- AGENT_TOOLS: tarea que requiere un agente con acceso a herramientas
- ORCHESTRATE: tarea compleja que necesita varios agentes coordinados

Contexto del módulo: {module_context}
Mensaje del usuario: {message}

Responde SOLO con el nombre del modo, sin explicación."""
            }],
            max_tokens=20
        )
        mode_str = response.content.strip().upper()
        return CopilotMode(mode_str.lower()) if mode_str.lower() in CopilotMode.__members__ else CopilotMode.CHAT_RAG
