# Extraído de: LibroTecnico/cap-13-busqueda-meilisearch.md
import re
import anthropic
from enum import Enum
from dataclasses import dataclass

class TipoIntent(str, Enum):
    CHAT_RAG = "CHAT_RAG"           # Consulta analítica → Qdrant + síntesis Claude
    AGENT_TOOLS = "AGENT_TOOLS"     # Búsqueda estructurada → Meilisearch
    WORKFLOW = "WORKFLOW"           # Instrucción de automatización → Workflow Engine
    OFF_TOPIC = "OFF_TOPIC"         # Fuera del dominio → rechazar con mensaje guía

@dataclass
class IntentResult:
    tipo: TipoIntent
    confianza: float       # 0.0 - 1.0
    subtipo: str = ""      # Información adicional para el handler
    razonamiento: str = "" # Solo cuando se usa la capa LLM

# --- CAPA 1: Pattern matching determinista ---

PATRONES_SEARCH_OPORTUNIDADES = [
    r'\b(busca|encuentra|muestra|lista|filtra)\b.{0,50}\b(oportunidad|contrato|licitaci|concurso)',
    r'\b(oportunidades?|contratos?)\b.{0,30}\b(con|en|de|para)\b.{0,50}\b(categor|presupuest|plazo)',
    # En producción se normaliza el texto (unidecode) antes del matching
    r'\b(qu[eé]\s+)?contratos?.{0,30}\b(tecnolog|ciberseg|consultor)',
]

PATRONES_RAG = [
    r'\b(explica|analiza|resume|comparar?|diferencia|cu[aá]les?.{0,20}(mejor|mayor|ventaj))',
    r'\b(propuesta|propuestas|documento|documentos|cv|curr[íi]cul)',
    r'\b(hist[oó]ric|antecedente|caso\s+similar|qu[eé]\s+hicimos)',
]

PATRONES_WORKFLOW = [
    r'\b(genera|crea|elabora|redacta|prepara)\b.{0,50}\b(propuesta|informe|documento)',
    r'\b(automatiza|ejecuta|lanza|procesa)\b',
    r'\b(workflow|flujo|proceso)\b',
]

PATRONES_OFF_TOPIC = [
    r'\b(tiempo|clima|deporte|noticias|pel[ií]cula|canci[oó]n)\b',
    r'\b(qu[eé]\s+es|define|definici[oó]n\s+de)\b.{0,30}\b(?!la\s+plataforma)',
]

UMBRAL_CONFIANZA_CAPA1 = 0.75


