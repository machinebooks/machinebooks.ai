# Extraído de: LibroTecnico/cap-11-integracion-llms.md
# Ejemplo didáctico: patrones/ai_service/llm_factory.py
from enum import Enum
from typing import Optional
from dataclasses import dataclass
import anthropic
import openai
from langchain_anthropic import ChatAnthropic
from langchain_openai import AzureChatOpenAI

class LLMProvider(str, Enum):
    ANTHROPIC = "anthropic"
    AZURE_OPENAI = "azure_openai"
    AZURE_AI_FOUNDRY = "azure_ai_foundry"  # Claude vía Azure
    OPENAI = "openai"
    OLLAMA = "ollama"
    LM_STUDIO = "lm_studio"

class TaskComplexity(str, Enum):
    HIGH = "high"      # → claude-opus-4-6
    MEDIUM = "medium"  # → claude-sonnet-4-6
    LOW = "low"        # → claude-haiku-4-5 o Ollama

@dataclass
class LLMRequest:
    service_type: str           # "document_analyzer", "proposal_generator", etc.
    task_complexity: TaskComplexity
    requires_local: bool = False  # True si hay restricción de privacidad
    user_id: Optional[str] = None
    correlation_id: Optional[str] = None

class LLMFactory:
    """
    Factoría central de clientes LLM.
    Desacopla los servicios de IA del proveedor concreto.
    """

    def __init__(self, config_service, budget_service, audit_service):
        self._config = config_service      # Lee LLMConfig de base de datos
        self._budget = budget_service      # Verifica límites de gasto
        self._audit = audit_service        # Registra cada llamada

    def get_client(self, request: LLMRequest) -> "LLMClient":
        """
        Devuelve el cliente correcto según políticas activas.
        Lanza ProviderUnavailableError si ningún proveedor puede servir la petición.
        """
        # 1. Verificar presupuesto antes de construir el cliente
        self._budget.check_or_raise(request.user_id, request.service_type)

        # 2. Seleccionar proveedor según políticas
        provider = self._select_provider(request)

        # 3. Construir cliente con modelo apropiado
        model_config = self._config.get_model_config(provider, request.task_complexity)

        # 4. Envolver en cliente con auditoría automática
        return AuditedLLMClient(
            inner=self._build_inner_client(provider, model_config),
            model_config=model_config,
            audit_service=self._audit,
            request=request
        )

    def _select_provider(self, request: LLMRequest) -> LLMProvider:
        """
        Política de selección: privacidad > disponibilidad > coste.
        """
        if request.requires_local:
            # Restricción de privacidad: solo inferencia local
            return LLMProvider.OLLAMA

        primary = self._config.get_primary_provider(request.service_type)

        if self._is_available(primary):
            return primary

        # Failover automático: seleccionar siguiente proveedor disponible
        for fallback in self._config.get_fallback_providers(primary):
            if self._is_available(fallback):
                self._audit.log_failover(request, primary, fallback)
                return fallback

        raise ProviderUnavailableError(
            f"Ningún proveedor disponible para {request.service_type}"
        )
