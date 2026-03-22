# Extraído de: LibroConsultor/cap-08-analisis-rfps.md
@dataclass
class EstimacionPropuesta:
    """Estimación del esfuerzo para preparar la propuesta."""
    horas_analisis_profundo: int    # Lectura detallada post go
    horas_redaccion_tecnica: int    # Propuesta técnica
    horas_documentacion: int         # CVs, referencias, certificados
    horas_revision_calidad: int      # Revisión por pares y dirección
    horas_maquetacion: int           # Formato final y firma
    horas_coordinacion_ute: int      # Si aplica
    total_horas: int
    perfiles_necesarios: list[str]   # Quién necesita participar
    coste_estimado_euros: float      # Horas * tarifa interna media
    plazo_critico: bool              # Si el plazo es ajustado

def estimar_esfuerzo_propuesta(
    score: ScoreGoNoGo,
    extracciones: dict,
    tarifa_interna_hora: float = 85.0
) -> EstimacionPropuesta:
    """Estima el esfuerzo de preparar la propuesta."""

    prompt = f"""Con base en el análisis de este RFP, estima el
esfuerzo de preparación de la propuesta.

SCORE: {score.puntuacion_global}/100
CRITERIOS DE VALORACIÓN: {extracciones['criterios_valoracion']}
PLAZOS: {extracciones['plazos_calendario']}
REQUISITOS NORMATIVOS: {extracciones['cumplimiento_normativo']}

Devuelve la estimación en formato JSON con los campos:
horas_analisis_profundo, horas_redaccion_tecnica,
horas_documentacion, horas_revision_calidad,
horas_maquetacion, horas_coordinacion_ute,
total_horas, perfiles_necesarios, plazo_critico.

Basa la estimación en:
- Propuestas de 60-80 páginas requieren 80-120 horas totales
- Propuestas de 30-50 páginas requieren 40-80 horas
- Criterios de juicio de valor aumentan la redacción un 30-50%
- UTEs añaden 15-25 horas de coordinación
- Plazos menores a 15 días incrementan las horas un 20% por
  la compresión y el trabajo en paralelo"""

    mensaje = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        system="Eres un director de operaciones de consultoría "
               "que estima esfuerzos de preparación de propuestas "
               "con precisión. Preferir sobreestimar a subestimar.",
        messages=[{"role": "user", "content": prompt}]
    )

    import json
    datos = json.loads(mensaje.content[0].text)
    datos["coste_estimado_euros"] = (
        datos["total_horas"] * tarifa_interna_hora
    )
    return EstimacionPropuesta(**datos)
