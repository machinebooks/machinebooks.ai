# Extraído de: LibroConsultor/cap-11-inteligencia-competitiva.md
import anthropic
import httpx
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Adjudicacion:
    """Estructura de una adjudicación pública recopilada."""
    titulo: str
    organismo: str
    adjudicatario: str
    importe: float
    fecha: datetime
    cpv: str           # Código de clasificación del contrato
    criterios: str     # Criterios de adjudicación publicados
    url_fuente: str

async def recopilar_adjudicaciones(
    cpv_codes: list[str],
    fecha_desde: str,
    fecha_hasta: str
) -> list[Adjudicacion]:
    """
    Consulta el portal de contratación pública y extrae
    adjudicaciones relevantes para los códigos CPV indicados.
    CPV 72000000 = servicios de TI y consultoría.
    """
    adjudicaciones = []
    async with httpx.AsyncClient() as client:
        for cpv in cpv_codes:
            # Consulta a la API de contratación pública
            response = await client.get(
                "https://contrataciondelestado.es/sindicacion/sindicacion_643/licitacionesPerfilContratante.atom",
                params={
                    "cpv": cpv,
                    "fechaDesde": fecha_desde,
                    "fechaHasta": fecha_hasta,
                    "estado": "ADJ"  # Solo adjudicaciones
                }
            )
            # Parseo del feed Atom y extracción estructurada
            adjudicaciones.extend(
                _parsear_feed_adjudicaciones(response.text)
            )
    return adjudicaciones
