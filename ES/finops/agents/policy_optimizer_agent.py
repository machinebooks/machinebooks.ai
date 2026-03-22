# Extraído de: LibroFinOps/cap-20-policy-as-code.md
# agents/policy_optimizer_agent.py
import anthropic
from services.policy_reconciler import PolicyReconciler

client = anthropic.Anthropic()

def generate_policy_optimization_proposals(db) -> list:
    """
    Analiza el uso de los últimos 30 días y propone ajustes.
    Las propuestas se presentan como borradores de PR.
    """
    usage_summary = get_usage_summary(db, days=30)
    current_policies = PolicyReconciler().get_all_policies()

    prompt = f"""
Eres un experto en gobernanza de costes de IA. Analiza los datos
de uso y las políticas actuales, y propón ajustes específicos que
optimicen el coste sin degradar la calidad del servicio.

**Datos de uso (últimos 30 días):**
{usage_summary}

**Políticas actuales (resumen):**
{current_policies}

**Genera máximo 3 propuestas con:**
1. Qué cambiar (campo YAML específico)
2. Valor actual vs. valor propuesto
3. Ahorro estimado
4. Riesgo de la propuesta (bajo/medio/alto)

Formato: JSON lista de propuestas.
"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )

    # Las propuestas se crean como PRs en draft
    return parse_proposals(response.content[0].text)
