# Extraído de: LibroDevSecOps/cap-12-dast-inteligente.md
def generate_api_fuzz_payloads(
    endpoint: dict,
    api_context: str,
) -> list[dict]:
    """Genera payloads de fuzzing contextualizados para un endpoint."""
    prompt = f"""Genera payloads de fuzzing para este endpoint de API:

Endpoint: {endpoint['method']} {endpoint['path']}
Parámetros: {json.dumps(endpoint['parameters'])}
Esquema del body: {json.dumps(endpoint.get('body_schema', {}))}
Contexto: {api_context}

Categorías de payloads a generar:
1. BOUNDARY: valores en los límites (0, -1, MAX_INT, strings vacíos,
   strings de 10.000 caracteres)
2. TYPE_CONFUSION: enviar tipo incorrecto (string donde espera int,
   array donde espera string)
3. INJECTION: SQL, NoSQL, command injection adaptados al tipo de campo
4. AUTH_BYPASS: manipulación de campos de autorización (IDOR con IDs
   de otros usuarios, roles elevados)
5. BUSINESS_LOGIC: valores válidos en formato pero inválidos en lógica
   (cantidades negativas, fechas futuras en campos de nacimiento)

Reglas:
- NO payloads destructivos (DELETE masivo, DROP)
- Payloads de detección, no de explotación
- Máximo 10 payloads por categoría
- Cada payload con la respuesta esperada si hay vulnerabilidad

Responde en JSON."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}],
    )
    return json.loads(message.content[0].text)
