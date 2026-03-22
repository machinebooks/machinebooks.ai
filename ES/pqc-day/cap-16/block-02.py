# Extraído de: LibroPQC/cap-16-dora.md
"""
Generador de explicaciones DORA-PQC auditables con Claude.
Transforma scores numéricos en narrativas que un auditor
o supervisor bancario puede evaluar.
"""
import anthropic
import json

client = anthropic.Anthropic()

AUDITOR_SYSTEM_PROMPT = """Eres un experto en regulación financiera europea
y criptografía post-cuántica. Generas explicaciones técnicas para
auditores DORA sobre la preparación PQC de entidades financieras.

Reglas:
- Referencia artículos específicos del Reglamento (UE) 2022/2554
- Menciona plazos regulatorios concretos (G7 CEG 2030-2032, NIST 2030/2035)
- Usa terminología de auditoría: "hallazgo", "evidencia", "control"
- Sé preciso con los algoritmos: ML-KEM (FIPS 203), ML-DSA (FIPS 204)
- No minimices ni exageres los riesgos
- Formato: párrafos cortos, lenguaje profesional, sin jerga innecesaria"""


def generate_audit_explanation(
    score: dict,
    findings_summary: dict,
    entity_profile: dict,
) -> str:
    """
    Genera una explicación auditable del score DORA-PQC
    para inclusión en informes de cumplimiento.
    """
    context = {
        "score": score,
        "findings": findings_summary,
        "entity": entity_profile,
        "regulatory_deadlines": {
            "g7_ceg": "Sistemas críticos migrados 2030-2032",
            "nist_deprecation": "RSA/ECC deprecados 2030",
            "nist_prohibition": "RSA/ECC prohibidos 2035",
            "eu_inventory": "Inventario criptográfico dic 2026",
            "dora_effective": "En vigor desde 17 enero 2025",
        },
    }

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=3000,
        system=AUDITOR_SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": f"""Genera la explicación auditable para este
assessment DORA-PQC.

Contexto del assessment:
{json.dumps(context, indent=2, ensure_ascii=False)}

La explicación debe cubrir:
1. Estado actual de preparación PQC de la entidad
2. Hallazgos críticos con referencia a artículos DORA
3. Brechas identificadas respecto a plazos G7 CEG
4. Recomendaciones priorizadas con horizonte temporal
5. Riesgos residuales si no se actúa

Formato: texto estructurado para sección de informe de auditoría."""
        }],
    )

    return message.content[0].text


def generate_resilience_scenarios(
    findings: list,
    entity_type: str,
) -> list[dict]:
    """
    Genera escenarios de resiliencia post-cuántica para pruebas TLPT
    según Art. 26 DORA, basados en los hallazgos reales de la entidad.
    """
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        system="""Eres un experto en pruebas de resiliencia operativa
digital (DORA Art. 26) y criptoanálisis cuántico. Generas escenarios
de prueba TLPT realistas basados en la amenaza cuántica.""",
        messages=[{
            "role": "user",
            "content": f"""Para una entidad financiera de tipo
"{entity_type}", genera 5 escenarios de prueba de resiliencia
post-cuántica basados en estos hallazgos criptográficos reales:

{json.dumps(findings[:20], indent=2, ensure_ascii=False)}

Cada escenario debe incluir:
- nombre: título descriptivo
- threat_actor: perfil del atacante (estado-nación, crimen organizado)
- attack_vector: cómo se explota la debilidad cuántica
- affected_systems: qué sistemas se ven comprometidos
- business_impact: impacto en operaciones financieras
- detection_indicators: señales de compromiso
- recovery_actions: pasos de recuperación
- dora_articles: artículos DORA relevantes

Devuelve un array JSON con los 5 escenarios."""
        }],
    )

    try:
        return json.loads(message.content[0].text)
    except json.JSONDecodeError:
        return [{"error": "Escenarios requieren revisión manual"}]
