# Extraído de: LibroDevSecOps/cap-06-secretos.md
import anthropic
import json
from dataclasses import dataclass

@dataclass
class SecretFinding:
    file: str
    line: int
    pattern: str
    confidence: str  # "high", "medium", "low"
    reason: str
    recommendation: str

def analyze_diff_for_secrets(diff_content: str) -> list[SecretFinding]:
    """Analiza un diff de Git buscando secretos no obvios con Claude."""
    client = anthropic.Anthropic()

    system_prompt = """Eres un analista de seguridad especializado en detección
de secretos filtrados en código fuente. Tu tarea es analizar diffs de Git
y detectar secretos que las herramientas basadas en regex NO detectarían.

Busca específicamente:
1. Contraseñas como literales de cadena sin prefijo identificable
2. Tokens en formatos propietarios no estándar
3. Claves de cifrado codificadas en base64 o hexadecimal
4. Credenciales embebidas en URLs que no siguen patrones de conexión habituales
5. Valores de alta entropía asignados a variables cuyo nombre sugiere un secreto
6. Comentarios que contienen credenciales de prueba "temporales"

NO reportes:
- Hashes de commits Git
- UUIDs de identificación no sensibles
- Valores que son claramente placeholders (<set-in-vault>, xxxx, example)
- Checksums de ficheros (SHA-256 de dependencias)

Para cada hallazgo, responde en JSON con: file, line, pattern,
confidence (high/medium/low), reason, recommendation."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=system_prompt,
        messages=[{
            "role": "user",
            "content": f"Analiza este diff en busca de secretos:\n\n{diff_content}"
        }]
    )

    # Parsear la respuesta JSON del modelo
    findings = json.loads(message.content[0].text)
    return [SecretFinding(**f) for f in findings]
