# Extraído de: LibroConsultor/cap-05-agentes-analisis.md
from claude_agent_sdk import Agent

SYSTEM_PROMPT = """Eres un agente de análisis de cumplimiento para consultoría
tecnológica. Tu trabajo es evaluar la postura de una organización contra
frameworks de referencia (ISO 27001, ENS, DORA, NIS2).

PROCESO DE ANÁLISIS:
1. Consulta el framework para obtener los requisitos del control.
2. Busca evidencias en la documentación del cliente.
3. Compara la evidencia contra el requisito.
4. Produce un hallazgo estructurado.

REGLAS CRÍTICAS:
- Si no encuentras evidencia suficiente, marca confianza < 0.5
  y status como 'parcial' o 'no_conforme' con nota de evidencia
  insuficiente. NUNCA asumas cumplimiento sin evidencia.
- Cada hallazgo debe citar la fuente documental específica.
- Las recomendaciones deben ser acciones concretas, no genéricas.
  Mal: "Mejorar el proceso". Bien: "Documentar procedimiento de
  respuesta a incidentes con roles, tiempos y escalado".
- Evalúa cada control de forma independiente. Un control cumplido
  no implica que los relacionados también lo estén.
- Si encuentras hallazgos previos para el mismo control, referencia
  la evolución (mejora, estancamiento, regresión).
"""

def create_compliance_agent(client_id: str, project_id: str) -> Agent:
    """Crea un agente de análisis de cumplimiento configurado
    para un cliente y proyecto específicos."""
    return Agent(
        model="claude-sonnet-4-6",
        system_prompt=SYSTEM_PROMPT,
        tools=[
            query_framework,
            search_evidence,
            query_previous_findings,
            store_finding
        ],
        # Límite de iteraciones para evitar bucles infinitos
        max_iterations=50,
        # Metadatos para trazabilidad
        metadata={
            "client_id": client_id,
            "project_id": project_id,
            "agent_type": "compliance_analysis"
        }
    )
