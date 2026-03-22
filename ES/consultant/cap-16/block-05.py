# Extraído de: LibroConsultor/cap-16-roadmaps-ia.md
def generar_entregable_roadmap(
    assessment: dict,
    contexto: dict,
    historico: list[dict]
) -> dict:
    """Pipeline completo: assessment → roadmap → entregable."""
    # 1. Generar iniciativas con Claude
    iniciativas = generar_roadmap(assessment, contexto)

    # 2. Secuenciar respetando dependencias
    secuencia = secuenciar_iniciativas(iniciativas)

    # 3. Estimar recursos para cada iniciativa
    estimaciones = {}
    for ini in secuencia:
        estimaciones[ini.nombre] = estimar_recursos(
            ini, historico, contexto
        )

    # 4. Calcular inversión total por horizonte
    inversion = {}
    for horizonte in Horizonte:
        inversion[horizonte.value] = sum(
            estimaciones[i.nombre].presupuesto_medio
            for i in secuencia if i.horizonte == horizonte
        )

    # 5. Generar narrativa ejecutiva
    narrativa = _generar_resumen_ejecutivo(
        secuencia, estimaciones, inversion, contexto
    )

    return {
        "cliente": contexto.get("nombre_anonimizado", "Cliente"),
        "fecha": "2026-03-29",
        "nivel_actual": assessment.get("nivel_global"),
        "nivel_objetivo_12m": _calcular_nivel_objetivo(assessment),
        "iniciativas": [_serializar(i) for i in secuencia],
        "estimaciones": estimaciones,
        "inversion_por_horizonte": inversion,
        "resumen_ejecutivo": narrativa,
        "riesgos_principales": _extraer_riesgos_top(secuencia),
        "gobernanza": _generar_modelo_gobernanza(contexto)
    }
