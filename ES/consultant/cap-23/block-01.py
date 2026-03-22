# Extraído de: LibroConsultor/cap-23-confidencialidad.md
def classify_semantic(text: str) -> ClassificationResult:
    """Clasificación semántica con Claude para casos ambiguos."""
    client = anthropic.Anthropic()

    response = client.messages.create(
        model="claude-haiku-4-5",  # Modelo ligero para clasificación
        max_tokens=512,
        system="""Eres un clasificador de sensibilidad de datos para
consultoría. Evalúa el fragmento y responde en JSON con:
- level: "public", "internal", "confidential", "restricted"
- reasons: lista de razones de la clasificación
- entities_found: entidades sensibles detectadas

Criterios:
- RESTRICTED: datos personales, credenciales, vulnerabilidades críticas
- CONFIDENTIAL: información del cliente identificable, hallazgos de auditoría
- INTERNAL: metodología, patrones genéricos, plantillas
- PUBLIC: normativa, estándares, información publicada""",
        messages=[{"role": "user", "content": f"Clasifica:\n\n{text[:2000]}"}]
    )

    # Parsear respuesta JSON y construir ClassificationResult
    import json
    data = json.loads(response.content[0].text)
    level = SensitivityLevel(data["level"])
    route = {
        SensitivityLevel.PUBLIC: "api_direct",
        SensitivityLevel.INTERNAL: "api_direct",
        SensitivityLevel.CONFIDENTIAL: "api_sanitized",
        SensitivityLevel.RESTRICTED: "local_only",
    }
    return ClassificationResult(
        level=level,
        reasons=data.get("reasons", []),
        entities_found=data.get("entities_found", []),
        recommendation=route[level],
    )
