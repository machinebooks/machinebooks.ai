# Source: The Consultant and the Machine -- Chapter 11
# Pattern: Award tracking, talent analysis, market pipeline
import anthropic
import httpx
from dataclasses import dataclass
from datetime import datetime

@dataclass
class Adjudicacion:
    """Structure of a collected public procurement award."""
    titulo: str
    organismo: str
    adjudicatario: str
    importe: float
    fecha: datetime
    cpv: str           # Contract classification code
    criterios: str     # Published award criteria
    url_fuente: str

async def recopilar_adjudicaciones(
    cpv_codes: list[str],
    fecha_desde: str,
    fecha_hasta: str
) -> list[Adjudicacion]:
    """
    Queries the public procurement portal and extracts
    relevant awards for the indicated CPV codes.
    CPV 72000000 = IT services and consulting.
    """
    adjudicaciones = []
    async with httpx.AsyncClient() as client:
        for cpv in cpv_codes:
            # Query the public procurement API
            response = await client.get(
                "https://contrataciondelestado.es/sindicacion/sindicacion_643/licitacionesPerfilContratante.atom",
                params={
                    "cpv": cpv,
                    "fechaDesde": fecha_desde,
                    "fechaHasta": fecha_hasta,
                    "estado": "ADJ"  # Awards only
                }
            )
            # Parse Atom feed and structured extraction
            adjudicaciones.extend(
                _parsear_feed_adjudicaciones(response.text)
            )
    return adjudicaciones

# --- Block 2 ---

from claude_agent_sdk import Agent, tool

@tool
def analizar_ofertas_empleo(
    empresas: list[str],
    periodo_dias: int = 30
) -> dict:
    """
    Analyzes job postings published by competitor companies.
    Extracts strategy signals: profiles sought, technologies,
    locations, seniority level.
    Only processes information published on public portals.
    """
    señales = {}
    for empresa in empresas:
        ofertas = _buscar_ofertas_publicas(empresa, periodo_dias)
        señales[empresa] = {
            "total_ofertas": len(ofertas),
            "perfiles_predominantes": _clasificar_perfiles(ofertas),
            "tecnologias_mencionadas": _extraer_tecnologias(ofertas),
            "areas_expansion": _inferir_areas(ofertas),
            "nivel_inversion": _estimar_nivel_inversion(ofertas)
        }
    return señales

@tool
def detectar_cambios_web(
    urls: list[str],
    ultima_revision: str
) -> list[dict]:
    """
    Detects changes on competitor service pages.
    Compares current content with stored version.
    Only accesses public pages without authentication.
    """
    cambios = []
    for url in urls:
        contenido_actual = _obtener_contenido_publico(url)
        contenido_anterior = _recuperar_cache(url, ultima_revision)
        if contenido_actual != contenido_anterior:
            diff = _generar_diff_semantico(
                contenido_anterior, contenido_actual
            )
            cambios.append({
                "url": url,
                "tipo_cambio": diff["tipo"],  # new_service, price, team
                "resumen": diff["resumen"],
                "relevancia": diff["relevancia"]  # high, medium, low
            })
    return cambios

# Competitive signals agent configuration
agente_señales = Agent(
    model="claude-sonnet-4-6",
    tools=[analizar_ofertas_empleo, detectar_cambios_web],
    system="""You are a competitive intelligence analyst for a
    technology consulting firm. You analyze EXCLUSIVELY public
    information to detect strategic movements by competitors.

    Unbreakable ethical rules:
    - Only information voluntarily published by companies
    - No inferences about individual people
    - No access to systems requiring authentication
    - Always indicate the confidence level of your inferences
    """
)

# --- Block 3 ---

import anthropic
from datetime import datetime, timedelta

client = anthropic.Anthropic(api_key="<YOUR_API_KEY>")

def generar_radar_tecnologico(
    dominios: list[str],
    periodo: str = "semanal"
) -> dict:
    """
    Generates a technology radar based on public sources:
    technical blogs, regulatory publications, conferences.
    """
    fuentes_procesadas = []

    for dominio in dominios:
        # Collect recent articles and publications
        articulos = _buscar_publicaciones_recientes(
            dominio, periodo
        )
        # Collect regulatory changes
        regulacion = _buscar_cambios_regulatorios(
            dominio, periodo
        )
        fuentes_procesadas.append({
            "dominio": dominio,
            "articulos": articulos,
            "regulacion": regulacion
        })

    # Analysis with Claude: cross sources and detect trends
    mensaje = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": f"""Analyze the following sources and generate a
            structured technology radar.

            Sources: {fuentes_procesadas}

            For each identified trend, indicate:
            1. Name and brief description (2-3 sentences)
            2. Maturity level: emerging / in adoption / established
            3. Relevance for technology consulting (high/medium/low)
            4. Estimated window of opportunity
            5. Competitors already positioning
            6. Sources supporting the signal

            Group by: AI and automation, cloud and infrastructure,
            security and compliance, data and analytics.

            Only include trends with at least 2 independent
            supporting sources."""
        }]
    )

    return _parsear_radar(mensaje.content[0].text)

# --- Block 4 ---

from claude_agent_sdk import Agent, tool
from dataclasses import dataclass

@dataclass
class InformeCompetitivo:
    """Periodic competitive intelligence report."""
    fecha: str
    resumen_ejecutivo: str
    movimientos_competidores: list[dict]
    tendencias_mercado: list[dict]
    oportunidades_detectadas: list[dict]
    alertas_pricing: list[dict]
    recomendaciones: list[dict]

@tool
def cruzar_fuentes_competitivas(
    adjudicaciones: list[dict],
    señales_empleo: dict,
    radar_tecnologico: dict,
    historial_propuestas: list[dict]
) -> InformeCompetitivo:
    """
    Cross-references information from all sources to generate
    an integrated competitive report.

    Correlations it searches for:
    - Competitor hires profiles X + appears in awards for Y
    - Technology trend Z + client that tenders in that domain
    - Award price vs our historical price
    """
    # Cross-referencing logic is the system's core:
    # 1. Map competitor → services → prices → trend
    # 2. Map client → history → probable needs
    # 3. Map trend → opportunity → positioned competitors

    correlaciones = _ejecutar_correlaciones(
        adjudicaciones, señales_empleo,
        radar_tecnologico, historial_propuestas
    )

    return InformeCompetitivo(
        fecha=datetime.now().isoformat(),
        resumen_ejecutivo=correlaciones["resumen"],
        movimientos_competidores=correlaciones["competidores"],
        tendencias_mercado=correlaciones["tendencias"],
        oportunidades_detectadas=correlaciones["oportunidades"],
        alertas_pricing=correlaciones["pricing"],
        recomendaciones=correlaciones["recomendaciones"]
    )

agente_mercado = Agent(
    model="claude-opus-4-6",
    tools=[cruzar_fuentes_competitivas],
    system="""You are a senior market analyst for a technology
    consulting firm. Your job is to cross data from multiple
    public sources and generate actionable competitive intelligence.

    Principles:
    - Distinguish facts from inferences. Mark each conclusion with
      its confidence level: high (direct data), medium (inference
      with 2+ signals), low (inference with 1 signal).
    - Pricing recommendations are based on actual public
      procurement awards, not assumptions.
    - Never recommend predatory pricing. The goal is
      sustainable positioning, not winning at any cost.
    - Always note what information is missing to improve the analysis.
    """
)
