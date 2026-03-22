# Extraído de: LibroConsultor/cap-23-confidencialidad.md
import subprocess

def route_request(
    text: str,
    task: str,
    project_config: dict,
) -> str:
    """Enruta la petición según clasificación de sensibilidad."""

    # Paso 1: clasificación determinista
    level, entities = classify_deterministic(text)

    # Paso 2: si no se detectó nada, clasificación semántica
    if level == SensitivityLevel.PUBLIC and len(text) > 200:
        result = classify_semantic(text)
        level = result.level

    # Paso 3: enrutar según nivel
    if level == SensitivityLevel.RESTRICTED:
        # Solo procesamiento local con Ollama
        return process_local(text, task)

    elif level == SensitivityLevel.CONFIDENTIAL:
        # Sanitizar y enviar a API
        san_map = SanitizationMap()
        clean_text = sanitize_text(text, san_map)
        response = process_api(clean_text, task)
        return san_map.restore(response)

    else:
        # Público o interno: API directa
        return process_api(text, task)

def process_local(text: str, task: str) -> str:
    """Procesa con modelo local vía Ollama."""
    import requests
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "llama3:70b",
            "prompt": f"Tarea: {task}\n\nTexto:\n{text}",
            "stream": False,
        },
        timeout=120,
    )
    return response.json()["response"]

def process_api(text: str, task: str) -> str:
    """Procesa con Claude API."""
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": f"Tarea: {task}\n\nTexto:\n{text}",
        }],
    )
    return response.content[0].text
