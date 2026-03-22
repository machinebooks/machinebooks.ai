# Extraído de: LibroTecnico/cap-11-integracion-llms.md
# Ejemplo didáctico basado en: ai_service/services/llm_factory.py
import time

# Caches en memoria del proceso
_config_cache: dict = {}       # Configuración de servicios IA
_config_cache_ts: float = 0    # Timestamp de última carga
_prompt_cache: dict = {}       # Prompts del sistema

def get_service_config(service_type: str) -> dict | None:
    """
    Obtiene la configuración de un servicio IA desde el backend.
    Caché de 60 segundos: cambios en el panel Admin se reflejan
    en menos de un minuto sin reiniciar el servicio.
    """
    global _config_cache, _config_cache_ts

    # TTL de 60 segundos para configuración de servicios
    if time.time() - _config_cache_ts < 60 and service_type in _config_cache:
        return _config_cache[service_type]

    # Llamada HTTP al backend (solo cada 60s por servicio)
    data = _fetch_config_from_backend(service_type)
    if data:
        _config_cache[service_type] = data
        _config_cache_ts = time.time()
    return data

def get_prompt(prompt_key: str, default: str = "") -> str:
    """
    Obtiene un prompt desde la configuración en BD.
    TTL diferenciado:
      - agent.* → 30s (cambios frecuentes en desarrollo)
      - resto   → 300s (prompts estables en producción)
    """
    # Prompts de agentes: caché corto para iteración rápida
    cache_ttl = 30 if prompt_key.startswith("agent.") else 300

    if prompt_key in _prompt_cache:
        entry_ts = _prompt_cache_timestamps.get(prompt_key, 0)
        if time.time() - entry_ts < cache_ttl:
            return _prompt_cache[prompt_key]

    prompt_text = _fetch_prompt_from_backend(prompt_key)
    if prompt_text:
        _prompt_cache[prompt_key] = prompt_text
        _prompt_cache_timestamps[prompt_key] = time.time()
        return prompt_text

    return default
