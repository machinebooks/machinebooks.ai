# Extraído de: LibroConsultor/cap-16-roadmaps-ia.md
@dataclass
class EstimacionRecursos:
    equipo: dict[str, int]       # perfil → número de personas
    duracion_semanas: int
    presupuesto_bajo: float      # escenario conservador
    presupuesto_medio: float     # escenario probable
    presupuesto_alto: float      # escenario pesimista
    confianza: float             # 0.0 - 1.0

def estimar_recursos(
    iniciativa: Iniciativa,
    historico: list[dict],
    contexto: dict
) -> EstimacionRecursos:
    """Estima recursos basándose en proyectos similares."""
    client = anthropic.Anthropic()

    # Buscar proyectos análogos en el histórico
    proyectos_similares = _buscar_analogos(
        iniciativa, historico, top_k=5
    )

    prompt = f"""Estima recursos para esta iniciativa de IA:

    Iniciativa: {iniciativa.nombre}
    Descripción: {iniciativa.descripcion}
    Tipo: {iniciativa.tipo.value}
    Sector cliente: {contexto.get('sector')}

    Proyectos análogos completados (datos reales anonimizados):
    {_formatear_analogos(proyectos_similares)}

    Genera estimación con:
    - Equipo necesario (perfiles y número)
    - Duración en semanas
    - Presupuesto en tres escenarios (bajo/medio/alto)
    - Nivel de confianza (0.0-1.0) según calidad de los análogos

    REGLA: si hay menos de 3 análogos relevantes,
    confianza máxima = 0.5. Sé honesto con la incertidumbre."""

    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    return _parsear_estimacion(response.content[0].text)
