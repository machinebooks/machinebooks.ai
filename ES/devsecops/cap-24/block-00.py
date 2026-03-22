# Extraído de: LibroDevSecOps/cap-24-security-champions.md
import anthropic
from dataclasses import dataclass

# Contexto del equipo para respuestas personalizadas
@dataclass
class TeamContext:
    team_name: str
    stack: list[str]          # ["FastAPI", "React", "PostgreSQL"]
    active_policies: list[str]
    recent_findings: list[dict]

def build_system_prompt(ctx: TeamContext) -> str:
    """Genera system prompt con contexto del equipo."""
    stack_str = ", ".join(ctx.stack)
    policies_str = "\n".join(f"- {p}" for p in ctx.active_policies)
    return f"""Eres un asistente de seguridad para el equipo {ctx.team_name}.
Stack tecnológico: {stack_str}.

Políticas de seguridad activas:
{policies_str}

Reglas:
- Responde en español técnico.
- Usa ejemplos del stack del equipo, no genéricos.
- Si la pregunta requiere análisis de código en producción, indica
  que debe escalar al equipo de seguridad.
- Incluye siempre la referencia CWE cuando aplique.
- Máximo 300 palabras por respuesta."""

def security_qa_bot(question: str, ctx: TeamContext) -> str:
    """Bot de Q&A de seguridad para champions."""
    client = anthropic.Anthropic()

    # Incluir hallazgos recientes como contexto
    findings_context = ""
    if ctx.recent_findings:
        findings_context = "\n\nHallazgos recientes del equipo:\n"
        for f in ctx.recent_findings[:5]:
            findings_context += (
                f"- [{f['severity']}] {f['title']} "
                f"en {f['file']} (CWE-{f['cwe']})\n"
            )

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=build_system_prompt(ctx) + findings_context,
        messages=[{"role": "user", "content": question}]
    )
    return response.content[0].text
