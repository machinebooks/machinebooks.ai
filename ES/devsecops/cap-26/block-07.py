# Extraído de: LibroDevSecOps/cap-26-caso-pipeline.md
def run_targeted_dast(openapi_spec: dict, base_url: str) -> list[dict]:
    """Ejecuta DAST dirigido usando ZAP + agente Claude para payloads."""
    endpoints = extract_endpoints_with_params(openapi_spec)

    # El agente genera payloads específicos por endpoint
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": (
                f"Genera payloads de testing de seguridad para estos "
                f"endpoints. Para cada uno, incluye payloads de SQL "
                f"injection, XSS, path traversal y SSRF adaptados "
                f"al tipo de parámetro:\n\n"
                f"{json.dumps(endpoints[:20], indent=2)}"
            )
        }]
    )

    payloads = parse_payloads(response)

    # Ejecutar ZAP con payloads personalizados
    zap_results = []
    for endpoint, payload_set in payloads.items():
        result = zap_active_scan(base_url + endpoint, payload_set)
        zap_results.extend(result)

    return zap_results
