# Extraído de: LibroTecnico/cap-13-busqueda-meilisearch.md
import feedparser
import re
from datetime import datetime, timezone
from typing import Optional
from dataclasses import dataclass, field

# Taxonomía de categorías normalizada
CATEGORIA_MAP = {
    "tecnología": ["tecnolog", "informátic", "digital", "software", "hardware", "datos"],
    "consultoría": ["consultor", "asesor", "estudios", "análisis", "diseño"],
    "seguridad": ["seguridad", "cibersegur", "vigilanci", "protect"],
    "formación": ["formaci", "capacit", "training", "curso"],
    "servicios_prof": ["servicios profesionales", "asistencia técnica"],
}

@dataclass
class OportunidadNormalizada:
    """Documento normalizado listo para indexar en Meilisearch."""
    id: str                          # Identificador único de la fuente
    titulo: str
    descripcion: str
    organismo: str
    presupuesto_min: float = 0.0    # Para filtros de rango presupuestario
    presupuesto_max: float = 0.0
    categoria: str = "sin_categoria"
    tipo_contrato: str = "servicios"
    fecha_publicacion: str = ""     # ISO 8601 para ordenación
    fecha_limite: str = ""
    cpv_codes: list = field(default_factory=list)
    estado: str = "activo"
    relevancia_score: float = 0.0   # Puntuación precomputada según taxonomía
    fuente: str = ""


