# Extraído de: LibroTecnico/cap-13-busqueda-meilisearch.md
def parsear_feed_atom(url_feed: str, fuente_id: str) -> list[OportunidadNormalizada]:
    """
    Parsea un feed ATOM de portal de contratación pública.
    Normaliza campos heterogéneos a esquema común.
    """
    feed = feedparser.parse(url_feed)
    oportunidades = []

    for entrada in feed.entries:
        try:
            presupuesto = extraer_presupuesto(entrada)
            categoria = inferir_categoria(entrada.get("title", "") + " " + entrada.get("summary", ""))

            oportunidad = OportunidadNormalizada(
                id=f"{fuente_id}_{entrada.get('id', entrada.link).split('/')[-1]}",
                titulo=limpiar_texto(entrada.get("title", "")),
                descripcion=limpiar_texto(entrada.get("summary", ""))[:2000],
                organismo=extraer_organismo(entrada),
                presupuesto_min=presupuesto * 0.8,  # Tolerancia ±20% en filtros
                presupuesto_max=presupuesto * 1.2,
                categoria=categoria,
                fecha_publicacion=normalizar_fecha(entrada.get("published", "")),
                fecha_limite=normalizar_fecha(entrada.get("updated", "")),
                fuente=fuente_id,
                relevancia_score=calcular_relevancia(categoria, presupuesto),
            )
            oportunidades.append(oportunidad)
        except Exception as exc:
            # Registrar error sin detener el pipeline completo
            # — los feeds públicos frecuentemente tienen entradas malformadas
            log_ingesta_error(fuente_id, entrada.get("id", "desconocido"), str(exc))

    return oportunidades


