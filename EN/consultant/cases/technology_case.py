# Source: The Consultant and the Machine -- Chapter 27
# Pattern: Tech consulting: repo analysis, evaluation, estimation
import anthropic
import json
from pathlib import Path

client = anthropic.Anthropic(api_key="<YOUR_API_KEY>")

def analizar_estructura_servicio(nombre_servicio: str, metadatos: dict) -> dict:
    """Analyzes a service's structure from its metadata."""
    prompt = f"""You are a senior software architect evaluating a service
for a modernization project.

Service: {nombre_servicio}
Language: {metadatos['lenguaje']}
Lines of code: {metadatos['loc']}
External dependencies: {json.dumps(metadatos['dependencias'], indent=2)}
Database schema (tables and relationships): {json.dumps(metadatos['esquema_db'], indent=2)}
Quality metrics (SonarQube): {json.dumps(metadatos['sonar'], indent=2)}

Evaluate:
1. Coupling level with other services (high/medium/low) and evidence
2. Critical technical debt (that would block a migration)
3. Estimated migration complexity (1-5, where 5 is maximum)
4. Dependencies requiring replacement in a cloud-native architecture
5. Specific risks for this service during migration

Respond in structured JSON."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )
    return json.loads(message.content[0].text)

# Process all 12 services
resultados = {}
for servicio in servicios_cliente:
    metadatos = extraer_metadatos(servicio)
    resultados[servicio['nombre']] = analizar_estructura_servicio(
        servicio['nombre'], metadatos
    )

# --- Block 2 ---

from claude_agent_sdk import Agent, tool

@tool
def evaluar_alternativa_tecnologica(
    alternativa: str,
    criterios: list[dict],
    contexto_cliente: dict
) -> dict:
    """Evaluates a technology alternative against the client's weighted criteria.

    Args:
        alternativa: Alternative name (e.g., "microservices with Spring Boot")
        criterios: List of criteria with name, weight, and description
        contexto_cliente: Client constraints (cloud, team, regulation)
    """
    ...

agent = Agent(
    model="claude-sonnet-4-6",
    tools=[evaluar_alternativa_tecnologica],
    system="""You are a solutions architect experienced in legacy system
modernization in the financial/insurance sector. You evaluate technology
alternatives with concrete data, not opinions. When you lack sufficient
data, indicate the level of uncertainty."""
)

# --- Block 3 ---

def estimar_esfuerzo_migracion(
    servicio: dict,
    complejidad: int,
    historico_proyectos: list[dict]
) -> dict:
    """Estimates migration effort by analogy with historical projects."""

    prompt = f"""Based on these historical data from similar migrations:

{json.dumps(historico_proyectos, indent=2)}

Estimate the effort to migrate the following service:
- Name: {servicio['nombre']}
- LOC: {servicio['loc']}
- Complexity (1-5): {complejidad}
- Critical dependencies: {servicio['dependencias_criticas']}
- Current test coverage: {servicio['cobertura_tests']}%

Provide:
1. Optimistic, probable, and pessimistic estimates (in person-days)
2. Risk factors that could increase effort
3. Most analogous historical projects and why
4. Estimation confidence level (high/medium/low)

Use concrete data, not generalities."""

    message = client.messages.create(
        model="claude-opus-4-6",  # Opus for estimation — requires deep reasoning
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )
    return json.loads(message.content[0].text)
