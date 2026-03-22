# Extraído de: LibroConsultor/cap-12-auditorias-automatizadas.md
# Herramientas adicionales para auditoría de arquitectura
def analyze_architecture_doc(doc_content: str, criteria: list[str]) -> dict:
    """Analiza documentación de arquitectura contra criterios."""
    client = anthropic.Anthropic()

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=3000,
        messages=[{
            "role": "user",
            "content": f"""Analiza esta documentación de arquitectura
contra los siguientes criterios de calidad:

Criterios a evaluar:
{json.dumps(criteria, indent=2)}

Documentación:
{doc_content}

Para cada criterio, evalúa:
1. ¿Se aborda el criterio en la documentación?
2. ¿La solución propuesta es adecuada? ¿Por qué?
3. ¿Hay riesgos no mitigados?
4. ¿Hay alternativas mejores?

Responde en JSON con un array de evaluaciones."""
        }]
    )
    return json.loads(response.content[0].text)

# Criterios estándar de auditoría de arquitectura
ARCHITECTURE_CRITERIA = [
    "Separación de responsabilidades y modularidad",
    "Escalabilidad horizontal y vertical",
    "Resiliencia y tolerancia a fallos",
    "Gestión de secretos y credenciales",
    "Observabilidad: logs, métricas y trazas",
    "Estrategia de backup y recuperación",
    "Gestión de dependencias y actualizaciones",
    "Seguridad en comunicaciones entre servicios",
    "Estrategia de despliegue y rollback",
    "Documentación de decisiones de arquitectura (ADR)"
]
