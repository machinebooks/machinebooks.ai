# Extraído de: LibroConsultor/cap-27-caso-tecnologia.md
def estimar_esfuerzo_migracion(
    servicio: dict,
    complejidad: int,
    historico_proyectos: list[dict]
) -> dict:
    """Estima esfuerzo de migración por analogía con proyectos históricos."""

    prompt = f"""Con base en estos datos históricos de migraciones similares:

{json.dumps(historico_proyectos, indent=2)}

Estima el esfuerzo para migrar el siguiente servicio:
- Nombre: {servicio['nombre']}
- LOC: {servicio['loc']}
- Complejidad (1-5): {complejidad}
- Dependencias críticas: {servicio['dependencias_criticas']}
- Cobertura de tests actual: {servicio['cobertura_tests']}%

Proporciona:
1. Estimación optimista, probable y pesimista (en jornadas)
2. Factores de riesgo que podrían aumentar el esfuerzo
3. Proyectos históricos más análogos y por qué
4. Nivel de confianza de la estimación (alto/medio/bajo)

Usa datos concretos, no generalidades."""

    message = client.messages.create(
        model="claude-opus-4-6",  # Opus para estimación — requiere razonamiento profundo
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )
    return json.loads(message.content[0].text)
