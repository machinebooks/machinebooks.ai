# Extraído de: LibroTecnico/cap-13-busqueda-meilisearch.md
def indexar_oportunidades(oportunidades: list, client: meilisearch.Client):
    """
    Indexa un lote de oportunidades normalizadas.
    Meilisearch procesa la indexación de forma asíncrona;
    el método devuelve una tarea que puede monitorearse.
    """
    index = client.index(INDICE_OPORTUNIDADES)
    documentos = [asdict(op) for op in oportunidades]

    # Lotes de 1000 documentos — recomendación de la documentación oficial
    for i in range(0, len(documentos), 1000):
        lote = documentos[i:i+1000]
        tarea = index.add_documents(lote)
        # El ID de tarea permite verificar el estado de indexación
        print(f"Lote {i//1000 + 1}: tarea {tarea.task_uid}")
