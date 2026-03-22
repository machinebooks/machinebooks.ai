# Extraído de: LibroConsultor/cap-10-estimacion-esfuerzos.md
import anthropic
import numpy as np
from dataclasses import dataclass

@dataclass
class SimilitudProyecto:
    proyecto: ProyectoHistorico
    score_semantico: float  # 0-1, similitud de embeddings
    score_estructural: float  # 0-1, coincidencia de atributos
    score_combinado: float  # ponderación de ambos

def calcular_similitud_estructural(
    nuevo: dict, historico: ProyectoHistorico
) -> float:
    """Compara atributos discretos entre proyecto nuevo e histórico."""
    score = 0.0
    pesos = {
        "tipo_servicio": 0.30,
        "sector": 0.25,
        "complejidad_regulatoria": 0.20,
        "tecnologias": 0.25,
    }
    # Tipo de servicio: coincidencia exacta
    if nuevo["tipo_servicio"] == historico.tipo_servicio.value:
        score += pesos["tipo_servicio"]
    # Sector: coincidencia exacta
    if nuevo["sector"] == historico.sector:
        score += pesos["sector"]
    # Complejidad regulatoria: penalizar diferencia
    niveles = {"baja": 1, "media": 2, "alta": 3}
    diff = abs(
        niveles[nuevo["complejidad_regulatoria"]]
        - niveles[historico.complejidad_regulatoria.value]
    )
    score += pesos["complejidad_regulatoria"] * max(0, 1 - diff * 0.5)
    # Tecnologías: Jaccard similarity
    set_nuevo = set(nuevo.get("tecnologias", []))
    set_hist = set(historico.tecnologias)
    if set_nuevo | set_hist:
        jaccard = len(set_nuevo & set_hist) / len(set_nuevo | set_hist)
        score += pesos["tecnologias"] * jaccard
    return score
