# Extraído de: LibroPQC/cap-11-analisis-semantico.md
def _parse_ai_response(self, response_text: str) -> Dict:
    """Parsear respuesta de IA a JSON con degradación gradual"""
    # Intento 1: parseo directo
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass

    # Intento 2: extraer bloque JSON del texto
    json_match = re.search(r'\{[\s\S]*\}', response_text)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

    # Intento 3: retornar estructura vacía (no silenciar el fallo)
    logger.warning("Could not parse AI response as JSON")
    return {
        'findings': [],
        'summary': response_text[:500],
        'risk_score': 0,
        'quantum_vulnerable': [],
        'pqc_migration_plan': [],
        'recommendations': ['Could not parse AI response']
    }
