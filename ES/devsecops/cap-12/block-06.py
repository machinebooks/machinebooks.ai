# Extraído de: LibroDevSecOps/cap-12-dast-inteligente.md
def analyze_dast_results(
    zap_results: dict,
    api_surface: dict,
    scan_plan: dict,
) -> dict:
    """Analiza resultados de ZAP con Claude para filtrar falsos positivos."""
    # Agrupar alertas por endpoint y severidad
    alerts = zap_results.get("site", [{}])[0].get("alerts", [])

    alert_summary = []
    for alert in alerts:
        alert_summary.append({
            "name": alert.get("name"),
            "risk": alert.get("riskdesc", "").split(" ")[0],
            "confidence": alert.get("confidence"),
            "url": alert.get("instances", [{}])[0].get("uri", ""),
            "param": alert.get("instances", [{}])[0].get("param", ""),
            "evidence": alert.get("instances", [{}])[0].get("evidence", "")[:200],
            "cwe_id": alert.get("cweid"),
            "description": alert.get("desc", "")[:300],
            "count": len(alert.get("instances", [])),
        })

    prompt = f"""Eres un analista de seguridad experto revisando resultados de DAST.

Contexto de la aplicación:
- API REST con {api_surface['total_endpoints']} endpoints
- Autenticación: JWT Bearer token
- Framework: FastAPI con SQLAlchemy (ORM con prepared statements)
- Base de datos: PostgreSQL

Alertas de ZAP ({len(alert_summary)} tipos de alerta):
{json.dumps(alert_summary, indent=2)}

Para cada alerta, clasifica como:
- REAL: vulnerabilidad confirmada con evidencia clara
- PROBABLE: requiere verificación manual pero hay indicios
- FALSO_POSITIVO: explica por qué no aplica en este contexto

Criterios de análisis:
1. Una alerta de SQL injection en una app con ORM y prepared statements
   es probablemente falso positivo salvo que la evidencia muestre SQL crudo
2. XSS en endpoints que devuelven JSON (no HTML) es falso positivo
3. SSRF requiere que la URL inyectada se resuelva - verificar evidencia
4. Errores 400/422 genéricos NO son evidencia de vulnerabilidad
5. Tiempos de respuesta anómalos SÍ pueden indicar time-based injection

Responde en JSON:
{{
  "findings": [
    {{
      "alert_name": "...",
      "classification": "REAL|PROBABLE|FALSO_POSITIVO",
      "confidence": 0.0-1.0,
      "reasoning": "...",
      "recommended_action": "...",
      "cwe": "CWE-xxx"
    }}
  ],
  "summary": {{
    "total_alerts": N,
    "real": N,
    "probable": N,
    "false_positives": N,
    "risk_rating": "CRITICAL|HIGH|MEDIUM|LOW"
  }}
}}"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    return json.loads(message.content[0].text)
