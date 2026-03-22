# Extraído de: LibroDevSecOps/cap-23-excepciones-deuda.md
REVIEW_PROMPT = """Eres un analista de seguridad que revisa excepciones activas.

## Excepción activa
- ID: {exception_id}
- Hallazgo: {finding_id} ({severity})
- CVE: {cve_id}
- Aprobada el: {approved_at}
- Expira el: {expires_at}
- Risk score original: {risk_score}
- Controles compensatorios: {controls}

## Cambios desde la última revisión
{changes_context}

## Instrucciones
1. Evalúa si los cambios alteran el riesgo residual.
2. Verifica si la vulnerabilidad tiene ahora parche disponible.
3. Verifica si han aparecido exploits públicos.
4. Recomienda: mantener, escalar o resolver.

Responde en JSON:
{{
  "conditions_changed": true|false,
  "new_risk_score": <int>,
  "recommendation": "renew|escalate|resolve",
  "reasoning": "<texto>"
}}"""


def review_exception_with_agent(
    exception: SecurityException,
    changes_context: str
) -> dict:
    """Revisa una excepción activa con contexto actualizado."""

    prompt = REVIEW_PROMPT.format(
        exception_id=exception.id,
        finding_id=exception.finding_id,
        severity=exception.severity.value,
        cve_id=exception.cve_id or "N/A",
        approved_at=exception.approved_at.isoformat(),
        expires_at=exception.expires_at.isoformat(),
        risk_score=exception.agent_risk_score,
        controls=json.dumps(exception.compensating_controls),
        changes_context=changes_context
    )

    message = client.messages.create(
        model="claude-haiku-4-5",  # Revisión rutinaria: Haiku basta
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    return json.loads(message.content[0].text)
