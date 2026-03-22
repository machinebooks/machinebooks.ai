# Extraído de: LibroTecnico/cap-24-documentacion-ia.md
def generar_runbook_incidencia(
    servicio: str,
    sintomas: List[str],
    diagnosticos: List[dict],
    procedimientos_recuperacion: List[dict]
) -> str:
    """
    Genera un runbook de incidencia a partir de los datos de diagnóstico
    extraídos del sistema de monitoreo.
    """
    client = anthropic.Anthropic()

    contexto = {
        "servicio": servicio,
        "sintomas_comunes": sintomas,
        "arboles_de_diagnostico": diagnosticos,
        "procedimientos_recuperacion": procedimientos_recuperacion,
        "dependencias": obtener_dependencias_servicio(servicio),
        "metricas_normales": obtener_baseline_metricas(servicio)
    }

    prompt = f"""Genera un runbook operativo para el servicio '{servicio}'.

Contexto técnico:
{json.dumps(contexto, ensure_ascii=False, indent=2)}

El runbook debe seguir esta estructura:
1. Descripción del servicio y su criticidad
2. Indicadores de alerta (cuándo consultar este runbook)
3. Árbol de diagnóstico: síntoma → posible causa → comando de diagnóstico → acción
4. Procedimientos de recuperación paso a paso, numerados
5. Escalado: cuándo y a quién escalar
6. Contactos de guardia y canales de comunicación [REDACTADO - completar con datos reales]
7. Registro de incidencias previas y resoluciones

Tono: directo y preciso. El lector está bajo presión. Cada paso debe ser ejecutable
sin ambigüedad. Los comandos deben ir en bloques de código. Indicar el tiempo
estimado de cada procedimiento."""

    mensaje = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )

    return mensaje.content[0].text
