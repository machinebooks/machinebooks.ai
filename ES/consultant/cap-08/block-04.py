# Extraído de: LibroConsultor/cap-08-analisis-rfps.md
def analizar_rfp_completo(
    ruta_pdf: str,
    perfil_firma: PerfilFirma
) -> dict:
    """Pipeline completo de análisis de RFP.

    Retorna el análisis estructurado con score go/no-go.
    Tiempo típico: 12-18 minutos para un RFP de 200-350 páginas.
    Coste típico: $5-15 en tokens de API.
    """
    # 1. Preprocesar documento
    documento = preprocesar_rfp(ruta_pdf)
    print(f"Documento: {documento.num_paginas} páginas procesadas")

    # 2. Extraer por categorías (en paralelo si el contexto lo permite)
    resultados_extraccion = {}
    coste_total_tokens = 0

    for cat, config in CATEGORIAS_EXTRACCION.items():
        print(f"Extrayendo: {cat}...")
        resultado = extraer_categoria(
            documento.texto_completo, cat, config
        )
        resultados_extraccion[cat] = resultado
        coste_total_tokens += (
            resultado["tokens_entrada"]
            + resultado["tokens_salida"]
        )

    # 3. Cruzar con capacidades de la práctica
    print("Cruzando con capacidades internas...")
    cruce = cruzar_requisitos_capacidades(
        resultados_extraccion["requisitos_obligatorios"],
        perfil_firma
    )

    # 4. Generar score go/no-go
    print("Generando puntuación go/no-go...")
    analisis = {
        "requisitos_cumplimiento": cruce,
        "criterios_encaje": resultados_extraccion["criterios_valoracion"],
        "riesgos": resultados_extraccion["riesgos_penalizaciones"],
        "plazos": resultados_extraccion["plazos_calendario"],
        "normativo": resultados_extraccion["cumplimiento_normativo"]
    }
    score = generar_score_go_nogo(analisis)

    # 5. Resumen de costes de análisis
    coste_api = coste_total_tokens * 0.000003  # Aproximación
    print(f"\nAnálisis completado. Tokens: {coste_total_tokens:,}")
    print(f"Coste estimado API: ${coste_api:.2f}")
    print(f"Recomendación: {score.recomendacion} "
          f"({score.puntuacion_global}/100)")

    return {
        "documento": documento,
        "extracciones": resultados_extraccion,
        "cruce_capacidades": cruce,
        "score": score,
        "coste_tokens": coste_total_tokens,
        "coste_api_usd": coste_api
    }
