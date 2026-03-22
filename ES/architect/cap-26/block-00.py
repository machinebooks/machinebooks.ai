# Extraído de: LibroTecnico/cap-26-desarrollador-futuro.md
# Ejemplo didáctico: registro de auditoría para cada llamada a modelo de lenguaje
# Patrón implementado en el servicio IA de la Plataforma

import hashlib
import time
from anthropic import Anthropic

client = Anthropic()

def llamar_modelo_con_trazabilidad(
    prompt: str,
    modelo: str = "claude-sonnet-4-6",
    tipo_tarea: str = "analisis_general",
    usuario_id: int | None = None
) -> dict:
    """
    Envuelve cada llamada al modelo con registro completo de auditoría.
    Permite reconstruir qué ocurrió, cuándo y con qué configuración.
    El hash del prompt evita almacenar PII mientras permite correlacionar llamadas.
    """
    hash_prompt = hashlib.sha256(prompt.encode()).hexdigest()
    inicio = time.time()

    respuesta = client.messages.create(
        model=modelo,
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}]
    )

    duracion_ms = int((time.time() - inicio) * 1000)

    # Registro estructurado para auditoría IA: qué modelo, cuándo, cuánto costó
    registro = {
        "modelo": modelo,
        "tipo_tarea": tipo_tarea,
        "usuario_id": usuario_id,
        "hash_prompt": hash_prompt,           # No guardamos el prompt completo si tiene PII
        "tokens_entrada": respuesta.usage.input_tokens,
        "tokens_salida": respuesta.usage.output_tokens,
        "latencia_ms": duracion_ms,
        "stop_reason": respuesta.stop_reason,
        "timestamp": time.time()
    }

    # Persistir en LLMUsageLog para trazabilidad completa y cálculo de ROI
    guardar_registro_uso_llm(registro)

    return {
        "contenido": respuesta.content[0].text,
        "auditoria": registro
    }
