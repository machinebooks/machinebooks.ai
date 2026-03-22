# Extraído de: LibroTecnico/cap-13-busqueda-meilisearch.md
from celery import shared_task

UMBRAL_INDEXACION_VECTORIAL = 7.0

@shared_task(queue="sync", rate_limit="100/m")
def indexar_oportunidad(oportunidad_dict: dict):
    """
    Tarea Celery para indexación dual (Meilisearch + Qdrant selectivo).
    La cola 'sync' limita a 100 indexaciones por minuto para no saturar
    el modelo de embedding durante picos de ingesta.
    """
    from search.meilisearch_setup import indexar_oportunidades
    from search.oportunidades_normalizer import OportunidadNormalizada
    import dataclasses

    oportunidad = OportunidadNormalizada(**oportunidad_dict)

    # Indexar siempre en Meilisearch (búsqueda textual rápida)
    indexar_oportunidades([oportunidad], get_meilisearch_client())

    # Indexar en Qdrant solo si supera el umbral de relevancia
    if oportunidad.relevancia_score >= UMBRAL_INDEXACION_VECTORIAL:
        vectorizar_e_indexar_qdrant(
            id=oportunidad.id,
            texto=f"{oportunidad.titulo}. {oportunidad.descripcion}",
            metadata=dataclasses.asdict(oportunidad),
            coleccion="oportunidades",
        )
