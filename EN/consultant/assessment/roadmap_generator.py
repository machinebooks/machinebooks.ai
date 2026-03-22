# Source: The Consultant and the Machine -- Chapter 16
# Pattern: AI roadmap: initiatives, prioritization, resources
import anthropic
from dataclasses import dataclass, field
from enum import Enum

class Horizonte(Enum):
    QUICK_WIN = "0-90 days"
    CONSOLIDACION = "3-12 months"
    TRANSFORMACION = "12-36 months"

class TipoAdquisicion(Enum):
    BUILD = "build"
    BUY = "buy"
    INTEGRATE = "integrate"

@dataclass
class Iniciativa:
    nombre: str
    descripcion: str
    horizonte: Horizonte
    impacto: int          # 1-5
    esfuerzo: int         # 1-5
    dependencias: list[str] = field(default_factory=list)
    riesgo: int = 3       # 1-5
    tipo: TipoAdquisicion = TipoAdquisicion.INTEGRATE
    presupuesto_min: float = 0.0
    presupuesto_max: float = 0.0
    equipo_necesario: list[str] = field(default_factory=list)
    kpi_exito: str = ""

    @property
    def prioridad(self) -> float:
        """Composite prioritization score."""
        n_deps = len(self.dependencias)
        return (self.impacto * 3
                - self.esfuerzo * 2
                - min(n_deps, 3) * 2
                - self.riesgo) / 8

def generar_roadmap(assessment: dict, contexto_cliente: dict) -> list[Iniciativa]:
    """Generates roadmap from assessment data and context."""
    client = anthropic.Anthropic()

    system_prompt = """You are a senior AI consultant specializing in
    adoption roadmaps. Generate concrete initiatives based on:

    RULES:
    - Quick wins: maximum 5 initiatives, all with demonstrable ROI in 90 days
    - Consolidation: 5-8 enabling infrastructure initiatives
    - Transformation: 3-5 high-impact strategic initiatives
    - Each initiative must have: name, description, impact (1-5),
      effort (1-5), dependencies, type (build/buy/integrate),
      budget range, required team, success KPI
    - Prioritize integrate over buy, buy over build (except for differentiation)

    PROVEN PATTERN CATALOG:
    - Level 1→2: FAQ chatbot, document automation, BI dashboards with AI
    - Level 2→3: data pipeline, basic MLOps, AI governance, internal RAG
    - Level 3→4: custom models, autonomous agents, AI embedded in product
    - Level 4→5: AI as competitive advantage, agent ecosystem, innovation
    """

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": f"""Client assessment:
    - Sector: {contexto_cliente.get('sector', 'not specified')}
    - Size: {contexto_cliente.get('empleados', 'N/A')} employees
    - Annual IT budget: {contexto_cliente.get('presupuesto_it', 'N/A')}
    - Risk appetite: {contexto_cliente.get('apetito_riesgo', 'moderate')}

    Maturity scores (1-5):
    - Data: {assessment.get('datos', 0)}
    - Infrastructure: {assessment.get('infraestructura', 0)}
    - Talent: {assessment.get('talento', 0)}
    - Governance: {assessment.get('gobernanza', 0)}
    - Use cases: {assessment.get('casos_uso', 0)}

    Overall level: {assessment.get('nivel_global', 0)}

    Generate the complete roadmap in structured JSON format."""}]
    )

    return _parsear_iniciativas(response.content[0].text)

# --- Block 2 ---

from collections import defaultdict, deque

def secuenciar_iniciativas(iniciativas: list[Iniciativa]) -> list[Iniciativa]:
    """Orders initiatives respecting dependencies and maximizing priority."""
    nombre_a_ini = {i.nombre: i for i in iniciativas}
    grafo = defaultdict(list)
    grado_entrada = defaultdict(int)

    for ini in iniciativas:
        if ini.nombre not in grado_entrada:
            grado_entrada[ini.nombre] = 0
        for dep in ini.dependencias:
            if dep in nombre_a_ini:
                grafo[dep].append(ini.nombre)
                grado_entrada[ini.nombre] += 1

    # Topological sort with priority (Kahn + heap)
    import heapq
    cola = []
    for nombre, grado in grado_entrada.items():
        if grado == 0:
            ini = nombre_a_ini[nombre]
            heapq.heappush(cola, (-ini.prioridad, nombre))

    resultado = []
    while cola:
        _, nombre = heapq.heappop(cola)
        resultado.append(nombre_a_ini[nombre])
        for sucesor in grafo[nombre]:
            grado_entrada[sucesor] -= 1
            if grado_entrada[sucesor] == 0:
                ini_suc = nombre_a_ini[sucesor]
                heapq.heappush(cola, (-ini_suc.prioridad, sucesor))

    # Detect cycles
    if len(resultado) != len(iniciativas):
        ciclo = [i.nombre for i in iniciativas
                 if i.nombre not in {r.nombre for r in resultado}]
        raise ValueError(f"Circular dependencies detected: {ciclo}")

    return resultado

# --- Block 3 ---

def recomendar_tipo_adquisicion(
    iniciativa: dict,
    contexto_cliente: dict
) -> TipoAdquisicion:
    """Recommends build/buy/integrate based on client criteria."""
    es_diferencial = iniciativa.get("diferenciacion_negocio", False)
    tiene_equipo = contexto_cliente.get("equipo_ml_interno", 0) >= 3
    datos_propios = iniciativa.get("requiere_datos_propios", False)
    urgencia_alta = iniciativa.get("time_to_value_dias", 180) < 90
    presupuesto_limitado = contexto_cliente.get("restriccion_presupuesto", False)
    regulacion_estricta = contexto_cliente.get("sector_regulado", False)

    # Rule 1: if differential and team exists, build
    if es_diferencial and tiene_equipo and datos_propios:
        return TipoAdquisicion.BUILD

    # Rule 2: if urgent or limited budget, integrate API
    if urgencia_alta or (presupuesto_limitado and not es_diferencial):
        return TipoAdquisicion.INTEGRATE

    # Rule 3: if regulation demands data control, build or buy on-premise
    if regulacion_estricta and datos_propios:
        return TipoAdquisicion.BUILD if tiene_equipo else TipoAdquisicion.BUY

    # Rule 4: default to buy if mature solutions exist
    if iniciativa.get("soluciones_mercado_maduras", 0) >= 3:
        return TipoAdquisicion.BUY

    # Rule 5: integrate as fallback
    return TipoAdquisicion.INTEGRATE
