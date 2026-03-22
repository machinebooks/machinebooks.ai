# Extraído de: LibroTecnico/cap-13-busqueda-meilisearch.md
    resultado = index.search(
        consulta,
        {
            "filter": filtro_final,
            "sort": ["relevancia_score:desc", "fecha_publicacion:desc"],
            "limit": por_pagina,
            "offset": (pagina - 1) * por_pagina,
            # Resaltar términos coincidentes en el resultado
            "attributesToHighlight": ["titulo", "descripcion"],
            "highlightPreTag": "<mark>",
            "highlightPostTag": "</mark>",
        }
    )

    return {
        "total": resultado["estimatedTotalHits"],
        "pagina": pagina,
        "por_pagina": por_pagina,
        "resultados": resultado["hits"],
        "tiempo_ms": resultado["processingTimeMs"],
    }
