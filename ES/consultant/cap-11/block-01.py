# Extraído de: LibroConsultor/cap-11-inteligencia-competitiva.md
from claude_agent_sdk import Agent, tool

@tool
def analizar_ofertas_empleo(
    empresas: list[str],
    periodo_dias: int = 30
) -> dict:
    """
    Analiza ofertas de empleo publicadas por empresas competidoras.
    Extrae señales de estrategia: perfiles buscados, tecnologías,
    ubicaciones, nivel de seniority.
    Solo procesa información publicada en portales públicos.
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
    Detecta cambios en las páginas de servicios de competidores.
    Compara contenido actual con la versión almacenada.
    Solo accede a páginas públicas sin autenticación.
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
                "tipo_cambio": diff["tipo"],  # nuevo_servicio, precio, equipo
                "resumen": diff["resumen"],
                "relevancia": diff["relevancia"]  # alta, media, baja
            })
    return cambios

# Configuración del agente de señales competitivas
agente_señales = Agent(
    model="claude-sonnet-4-6",
    tools=[analizar_ofertas_empleo, detectar_cambios_web],
    system="""Eres un analista de inteligencia competitiva para una
    consultora tecnológica. Analizas información EXCLUSIVAMENTE pública
    para detectar movimientos estratégicos de competidores.

    Reglas éticas inquebrantables:
    - Solo información publicada voluntariamente por las empresas
    - No inferencias sobre personas individuales
    - No acceso a sistemas que requieran autenticación
    - Señala siempre el nivel de confianza de tus inferencias
    """
)
