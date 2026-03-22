# Extraído de: LibroTecnico/cap-13-busqueda-meilisearch.md
    # Ranking personalizado: primero por relevancia textual,
    # luego por puntuación de afinidad precomputada
    index.update_ranking_rules([
        "words",        # Coincidencia de palabras
        "typo",         # Tolerancia a errores tipográficos
        "proximity",    # Proximidad de términos en el documento
        "attribute",    # Peso del campo donde aparece la coincidencia
        "sort",         # Ordenación explícita del usuario
        "exactness",    # Coincidencia exacta vs parcial
    ])

    # Campos que aparecen en la respuesta pero no en la búsqueda
    # — mejora rendimiento excluyendo textos largos del índice de búsqueda
    index.update_displayed_attributes([
        "id", "titulo", "descripcion", "organismo",
        "categoria", "tipo_contrato", "presupuesto_max",
        "fecha_publicacion", "fecha_limite", "relevancia_score",
        "fuente", "estado",
    ])

    print(f"Índice '{INDICE_OPORTUNIDADES}' configurado correctamente.")


