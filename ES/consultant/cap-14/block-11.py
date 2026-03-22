# Extraído de: LibroConsultor/cap-14-reporting.md
from datetime import datetime

def generar_informe_progreso(
    proyecto: ProyectoReporting,
    hallazgos_actualizados: list[dict],
    periodo: str,
    voice_prompt: str
) -> str:
    """Genera informe de progreso semanal/mensual."""

    # Clasificar hallazgos por estado actual
    resueltos = [h for h in hallazgos_actualizados
                 if h["estado"] == "resuelto"]
    en_progreso = [h for h in hallazgos_actualizados
                   if h["estado"] == "en_progreso"]
    pendientes = [h for h in hallazgos_actualizados
                  if h["estado"] == "pendiente"]
    bloqueados = [h for h in hallazgos_actualizados
                  if h["estado"] == "bloqueado"]

    prompt = f"""Genera un informe de progreso para el periodo
{periodo}.

PROYECTO: {proyecto.nombre_proyecto}
FECHA: {datetime.now().strftime('%Y-%m-%d')}

ESTADO ACTUAL:
- Resueltos: {len(resueltos)} de {len(hallazgos_actualizados)}
- En progreso: {len(en_progreso)}
- Pendientes: {len(pendientes)}
- Bloqueados: {len(bloqueados)}

HALLAZGOS BLOQUEADOS:
{chr(10).join(f"- {h['titulo']}: {h['motivo_bloqueo']}"
              for h in bloqueados)}

HALLAZGOS RESUELTOS EN ESTE PERIODO:
{chr(10).join(f"- {h['titulo']}" for h in resueltos
              if h.get('fecha_resolucion', '').startswith(periodo[:7]))}

INSTRUCCIONES:
1. Extensión: 300-500 palabras.
2. Abrir con porcentaje de avance global.
3. Destacar logros del periodo.
4. Alertar sobre bloqueos con propuesta de desbloqueo.
5. Indicar riesgos de desviación sobre el roadmap original.
6. Cerrar con acciones requeridas del cliente (si las hay).
7. Tono: informativo y directo, sin alarmismo."""

    response = client.messages.create(
        model="claude-haiku-4-5",  # Haiku para informes breves
        max_tokens=1024,
        system=voice_prompt,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text
