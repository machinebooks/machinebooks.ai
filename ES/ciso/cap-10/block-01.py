# Extraído de: LibroCISO/cap-10-arquitectura-llm.md
import anthropic
import openai
import httpx
import time
import logging
from typing import Optional
from functools import lru_cache
from datetime import datetime, timedelta

from app.models.ai import AIProvider, AIServiceConfig, ProviderType
from app.services.ai_cost_tracker import record_usage

logger = logging.getLogger(__name__)

# Caché de clientes con TTL para evitar crear conexiones en cada llamada
_client_cache: dict[str, tuple[object, datetime]] = {}
_CACHE_TTL = timedelta(minutes=10)


class LLMFactory:
    """Factory que crea clientes LLM dinámicamente desde configuración en BD."""

    def __init__(self, db_session):
        self.db = db_session

    def get_service_config(self, service_name: str) -> AIServiceConfig:
        """Obtiene la configuración activa de un servicio."""
        config = self.db.query(AIServiceConfig).filter(
            AIServiceConfig.service_name == service_name,
            AIServiceConfig.is_active == True
        ).first()
        if not config:
            raise ValueError(f"Servicio de IA '{service_name}' no configurado o inactivo")
        return config

    def _create_client(self, provider: AIProvider):
        """Crea un cliente para el proveedor especificado."""
        cache_key = f"{provider.name}_{provider.id}"
        now = datetime.now(timezone.utc)()

        # Comprobar caché
        if cache_key in _client_cache:
            client, cached_at = _client_cache[cache_key]
            if now - cached_at < _CACHE_TTL:
                return client

        # Crear cliente nuevo según el tipo de proveedor
        api_key = self._get_api_key(provider.api_key_ref) if provider.api_key_ref else None

        if provider.provider_type == ProviderType.ANTHROPIC:
            client = anthropic.Anthropic(api_key=api_key)

        elif provider.provider_type == ProviderType.OPENAI:
            client = openai.OpenAI(api_key=api_key)

        elif provider.provider_type == ProviderType.AZURE_OPENAI:
            client = openai.AzureOpenAI(
                api_key=api_key,
                azure_endpoint=provider.api_base_url,
                api_version="2024-06-01"
            )

        elif provider.provider_type == ProviderType.OLLAMA:
            # Ollama expone una API compatible con OpenAI
            client = openai.OpenAI(
                base_url=provider.api_base_url or "http://ollama:11434/v1",
                api_key="ollama"  # Ollama no requiere API key real
            )

        elif provider.provider_type == ProviderType.LM_STUDIO:
            client = openai.OpenAI(
                base_url=provider.api_base_url or "http://lm-studio:1234/v1",
                api_key="lm-studio"
            )
        else:
            raise ValueError(f"Tipo de proveedor no soportado: {provider.provider_type}")

        _client_cache[cache_key] = (client, now)
        return client

    def _call_provider(
        self,
        provider: AIProvider,
        model_name: str,
        messages: list[dict],
        config: AIServiceConfig,
        system_prompt: Optional[str] = None
    ) -> dict:
        """Ejecuta una llamada a un proveedor específico."""
        client = self._create_client(provider)
        start_time = time.time()

        try:
            if provider.provider_type == ProviderType.ANTHROPIC:
                # API de Anthropic: system prompt separado
                response = client.messages.create(
                    model=model_name,
                    max_tokens=config.max_output_tokens,
                    temperature=config.temperature,
                    system=system_prompt or "",
                    messages=messages
                )
                content = response.content[0].text
                input_tokens = response.usage.input_tokens
                output_tokens = response.usage.output_tokens

            else:
                # API compatible OpenAI (OpenAI, Azure, Ollama, LM Studio)
                full_messages = []
                if system_prompt:
                    full_messages.append({"role": "system", "content": system_prompt})
                full_messages.extend(messages)

                response = client.chat.completions.create(
                    model=model_name,
                    max_tokens=config.max_output_tokens,
                    temperature=config.temperature,
                    messages=full_messages
                )
                content = response.choices[0].message.content
                input_tokens = response.usage.prompt_tokens
                output_tokens = response.usage.completion_tokens

            latency_ms = int((time.time() - start_time) * 1000)

            # Registrar uso y coste
            record_usage(
                db=self.db,
                service_name=config.service_name,
                provider_name=provider.name,
                model_name=model_name,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                latency_ms=latency_ms,
            )

            return {
                "content": content,
                "provider": provider.name,
                "model": model_name,
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "latency_ms": latency_ms,
                "fallback_used": False
            }

        except Exception as e:
            latency_ms = int((time.time() - start_time) * 1000)
            logger.warning(
                f"Error en proveedor {provider.name}/{model_name}: {e} "
                f"(latencia: {latency_ms}ms)"
            )
            raise

    def call(
        self,
        service_name: str,
        messages: list[dict],
        system_prompt: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> dict:
        """
        Punto de entrada principal. Llama al proveedor configurado
        para el servicio, con fallback automático si falla.
        """
        config = self.get_service_config(service_name)

        # Aplicar guardrails de entrada
        self._apply_input_guardrails(config, messages)

        # Resolver prompt del sistema
        if system_prompt is None and config.active_prompt:
            system_prompt = config.active_prompt.prompt_text

        # Intentar proveedor principal
        try:
            result = self._call_provider(
                provider=config.provider,
                model_name=config.model_name,
                messages=messages,
                config=config,
                system_prompt=system_prompt
            )
            return self._apply_output_guardrails(config, result)

        except Exception as primary_error:
            logger.warning(f"Fallo en proveedor principal para {service_name}: {primary_error}")

            # Intentar fallback nivel 1 (cloud secundario)
            if config.fallback_provider_id:
                try:
                    fallback_provider = self.db.query(AIProvider).get(
                        config.fallback_provider_id
                    )
                    result = self._call_provider(
                        provider=fallback_provider,
                        model_name=config.fallback_model_name,
                        messages=messages,
                        config=config,
                        system_prompt=system_prompt
                    )
                    result["fallback_used"] = True
                    result["fallback_level"] = 1
                    logger.info(f"Fallback nivel 1 exitoso para {service_name}")
                    return self._apply_output_guardrails(config, result)

                except Exception as fallback_error:
                    logger.warning(f"Fallo en fallback nivel 1: {fallback_error}")

            # Intentar fallback nivel 2 (local)
            if config.local_fallback_provider_id:
                try:
                    local_provider = self.db.query(AIProvider).get(
                        config.local_fallback_provider_id
                    )
                    result = self._call_provider(
                        provider=local_provider,
                        model_name=config.local_fallback_model_name,
                        messages=messages,
                        config=config,
                        system_prompt=system_prompt
                    )
                    result["fallback_used"] = True
                    result["fallback_level"] = 2
                    result["degraded_mode"] = True
                    logger.info(f"Fallback nivel 2 (local) exitoso para {service_name}")
                    return self._apply_output_guardrails(config, result)

                except Exception as local_error:
                    logger.error(f"Fallo en todos los niveles de fallback: {local_error}")

            # Todos los niveles fallaron
            raise RuntimeError(
                f"Todos los proveedores fallaron para el servicio '{service_name}'. "
                f"Principal: {primary_error}"
            )

    def _apply_input_guardrails(self, config: AIServiceConfig, messages: list[dict]):
        """Evalúa guardrails de entrada antes de enviar al LLM."""
        guardrails = config.guardrails or {}

        # Límite de caracteres
        max_chars = guardrails.get("max_input_chars")
        if max_chars:
            total_chars = sum(len(m.get("content", "")) for m in messages)
            if total_chars > max_chars:
                raise ValueError(
                    f"Entrada excede el límite de {max_chars} caracteres "
                    f"({total_chars} recibidos)"
                )

        # Verificación de prompt injection
        if guardrails.get("prompt_injection_check", False):
            last_message = messages[-1].get("content", "") if messages else ""
            if self._detect_prompt_injection(last_message):
                raise SecurityError(
                    "Posible intento de prompt injection detectado. "
                    "La solicitud ha sido bloqueada."
                )

        # Filtro de PII
        if guardrails.get("enable_pii_filter", False):
            for msg in messages:
                if msg.get("role") == "user":
                    msg["content"] = self._mask_pii(msg.get("content", ""))

    def _apply_output_guardrails(self, config: AIServiceConfig, result: dict) -> dict:
        """Evalúa guardrails de salida sobre la respuesta del LLM."""
        guardrails = config.guardrails or {}

        # Filtro de PII en salida
        if guardrails.get("enable_pii_filter", False):
            result["content"] = self._mask_pii(result["content"])

        return result

    def _detect_prompt_injection(self, text: str) -> bool:
        """
        Detección heurística de prompt injection.
        Aplica normalización Unicode (NFKC) antes del matching
        para prevenir bypass con homoglifos o caracteres fullwidth.
        En producción se complementa con un clasificador dedicado.
        """
        import unicodedata
        # Normalizar Unicode para detectar homoglifos y trucos de codificación
        normalized = unicodedata.normalize("NFKC", text)
        text_lower = normalized.lower()

        injection_patterns = [
            "ignore previous instructions",
            "ignore all previous",
            "disregard your instructions",
            "you are now",
            "new instructions:",
            "system prompt:",
            "olvida las instrucciones",
            "ignora las instrucciones anteriores",
        ]
        return any(pattern in text_lower for pattern in injection_patterns)

    def _mask_pii(self, text: str) -> str:
        """
        Enmascara datos personales detectados en el texto.
        Detecta: DNI/NIE, IBAN, tarjetas de crédito, emails, teléfonos.
        """
        import re
        # DNI español: 8 dígitos + letra
        text = re.sub(r'\b\d{8}[A-Za-z]\b', '[DNI_ENMASCARADO]', text)
        # NIE: X/Y/Z + 7 dígitos + letra
        text = re.sub(r'\b[XYZxyz]\d{7}[A-Za-z]\b', '[NIE_ENMASCARADO]', text)
        # IBAN español
        text = re.sub(r'\bES\d{22}\b', '[IBAN_ENMASCARADO]', text)
        # Tarjeta de crédito (16 dígitos con separadores opcionales)
        text = re.sub(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
                      '[TARJETA_ENMASCARADA]', text)
        # Email
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                      '[EMAIL_ENMASCARADO]', text)
        return text

    # Referencias de claves permitidas (whitelist)
    _ALLOWED_KEY_REFS = frozenset({
        "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY",
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT",
    })

    @staticmethod
    def _get_api_key(key_ref: str) -> str:
        """Recupera clave de API del vault seguro.

        En producción: HashiCorp Vault, AWS Secrets Manager o Azure Key Vault.
        key_ref se valida contra una whitelist para evitar lectura arbitraria
        de variables de entorno.
        """
        import os
        if key_ref not in LLMFactory._ALLOWED_KEY_REFS:
            raise ValueError(
                f"Referencia de clave inválida '{key_ref}'. "
                f"Permitidas: {', '.join(sorted(LLMFactory._ALLOWED_KEY_REFS))}"
            )
        value = os.environ.get(key_ref)
        if not value:
            raise RuntimeError(
                f"Variable de entorno '{key_ref}' es obligatoria pero no está definida."
            )
        return value


class SecurityError(Exception):
    """Error de seguridad en guardrails de IA."""
    pass
