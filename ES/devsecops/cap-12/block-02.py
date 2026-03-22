# Extraído de: LibroDevSecOps/cap-12-dast-inteligente.md
import anthropic
import json

client = anthropic.Anthropic()

def generate_scan_plan(api_surface: dict) -> dict:
    """Genera un plan de escaneo DAST dirigido con Claude."""
    prompt = f"""Analiza la siguiente superficie de ataque de una API REST
y genera un plan de escaneo DAST. Para cada endpoint, indica:
1. Vulnerabilidades a probar (de OWASP Top 10 y API Security Top 10)
2. Payloads específicos para cada parámetro según su tipo y contexto
3. Prioridad de escaneo (alta/media/baja) según exposición y riesgo
4. Respuestas esperadas que indicarían una vulnerabilidad real

Reglas de seguridad:
- NO generar payloads destructivos (DROP TABLE, DELETE masivo)
- NO generar payloads de exfiltración de datos reales
- Limitar inyecciones a detección, no a explotación completa

Superficie de ataque:
{json.dumps(api_surface, indent=2)}

Responde en JSON con la estructura:
{{
  "scan_plan": [
    {{
      "endpoint": "/api/...",
      "method": "POST",
      "priority": "alta",
      "tests": [
        {{
          "category": "sql_injection",
          "parameter": "email",
          "payloads": ["..."],
          "expected_vulnerable_response": "...",
          "expected_safe_response": "..."
        }}
      ]
    }}
  ]
}}"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    return json.loads(message.content[0].text)
