# Extraído de: LibroTecnico/cap-13-busqueda-meilisearch.md
import meilisearch
from dataclasses import asdict

MEILISEARCH_URL = "http://meilisearch:7700"  # URL interna del contenedor
MEILISEARCH_KEY = "<TU_MEILISEARCH_MASTER_KEY>"
INDICE_OPORTUNIDADES = "oportunidades"

def configurar_indice_oportunidades(client: meilisearch.Client):
    """
    Configura el índice con los atributos correctos para búsqueda,
    filtrado y ordenación. Ejecutar una sola vez al inicializar.
    """
    index = client.index(INDICE_OPORTUNIDADES)

    # Atributos sobre los que se realizará búsqueda de texto
    index.update_searchable_attributes([
        "titulo",
        "descripcion",
        "organismo",
        "categoria",
    ])

    # Atributos que pueden usarse en filtros (WHERE equivalente)
    index.update_filterable_attributes([
        "categoria",
        "tipo_contrato",
        "estado",
        "fuente",
        "cpv_codes",
        "presupuesto_min",
        "presupuesto_max",
        "fecha_publicacion",
        "fecha_limite",
    ])

    # Atributos que se pueden usar en ORDER BY
    index.update_sortable_attributes([
        "fecha_publicacion",
        "presupuesto_max",
        "relevancia_score",
    ])

