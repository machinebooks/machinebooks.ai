# Extraído de: LibroConsultor/cap-08-analisis-rfps.md
@dataclass
class ScoreGoNoGo:
    """Resultado del análisis go/no-go de un RFP."""
    puntuacion_global: float          # 0-100
    recomendacion: str                # "go" | "no-go" | "go-condicional"
    requisitos_criticos_cumplidos: int
    requisitos_criticos_total: int
    brechas_bloqueantes: list[str]
    brechas_mitigables: list[str]
    fortalezas_competitivas: list[str]
    riesgos_principales: list[str]
    esfuerzo_propuesta_horas: int     # Estimación de horas para preparar
    coste_estimado_propuesta: float   # En EUR
    probabilidad_estimada_ganar: str  # "alta" | "media" | "baja"
    justificacion: str                # Narrativa de 3-5 frases

PROMPT_SCORING = """Con base en el análisis completo de este RFP,
genera una evaluación go/no-go estructurada.

DATOS DE ENTRADA:
- Requisitos obligatorios y cumplimiento: {requisitos_cumplimiento}
- Criterios de valoración y encaje: {criterios_encaje}
- Riesgos y penalizaciones: {riesgos}
- Plazos y restricciones: {plazos}
- Cumplimiento normativo: {normativo}

REGLAS DE PUNTUACIÓN:
1. Si hay 1+ brecha bloqueante sin mitigación → no-go (puntuación < 30)
2. Si hay brechas mitigables pero factibles → go-condicional (30-65)
3. Si se cumplen todos los obligatorios y hay encaje con criterios
   de valoración → go (65-100)
4. La probabilidad de ganar depende del encaje con criterios de
   juicio de valor, no solo de cumplir los obligatorios
5. El esfuerzo de preparación de la propuesta es un coste que
   debe considerarse: si la probabilidad es baja y el esfuerzo
   alto, incluso un go técnico puede ser un no-go económico

Genera un JSON con la estructura ScoreGoNoGo.
Incluye una justificación narrativa de 3-5 frases que un socio
pueda leer en 30 segundos y entender la recomendación."""

def generar_score_go_nogo(
    analisis_completo: dict
) -> ScoreGoNoGo:
    """Genera la puntuación go/no-go a partir del análisis."""
    mensaje = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system="Eres un director de preventa con 15 años de "
               "experiencia en consultoría tecnológica. Evalúas "
               "oportunidades con rigor financiero: no presentarse "
               "a una licitación que no puedes ganar es tan "
               "importante como ganar las que sí puedes.",
        messages=[{
            "role": "user",
            "content": PROMPT_SCORING.format(**analisis_completo)
        }]
    )
    # Parsear respuesta JSON a ScoreGoNoGo
    import json
    datos = json.loads(mensaje.content[0].text)
    return ScoreGoNoGo(**datos)
