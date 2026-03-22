# Extraído de: LibroTecnico/cap-13-busqueda-meilisearch.md
def buscar_oportunidades(
    consulta: str,
    categoria: str = None,
    presupuesto_min: float = None,
    presupuesto_max: float = None,
    dias_plazo: int = 30,
    tipo_contrato: str = None,
    pagina: int = 1,
    por_pagina: int = 20,
) -> dict:
    """
    Búsqueda de oportunidades con filtros combinados.
    Latencia objetivo: < 10ms para consultas sin texto libre.
    """
    client = meilisearch.Client(MEILISEARCH_URL, MEILISEARCH_KEY)
    index = client.index(INDICE_OPORTUNIDADES)

    # Construir filtro dinámico
    filtros = ["estado = 'activo'"]

    # Validar contra lista blanca antes de interpolar en el filtro
    # para evitar filter injection en Meilisearch
    CATEGORIAS_VALIDAS = {"tecnología", "consultoría", "seguridad", "infraestructura", "formación"}
    if categoria and categoria.lower() in CATEGORIAS_VALIDAS:
        filtros.append(f"categoria = '{categoria}'")

    if presupuesto_min is not None:
        filtros.append(f"presupuesto_max >= {presupuesto_min}")

    if presupuesto_max is not None:
        filtros.append(f"presupuesto_min <= {presupuesto_max}")

    TIPOS_CONTRATO_VALIDOS = {"servicios", "suministros", "obras", "mixto", "concesión"}
    if tipo_contrato and tipo_contrato.lower() in TIPOS_CONTRATO_VALIDOS:
        filtros.append(f"tipo_contrato = '{tipo_contrato}'")

    # Filtro de plazo — solo oportunidades con fecha límite futura
    desde = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    filtros.append(f"fecha_limite >= '{desde}'")

    filtro_final = " AND ".join(filtros)

