# Extraído de: LibroConsultor/cap-11-inteligencia-competitiva.md
import anthropic

client = anthropic.Anthropic()

def analizar_cambio_regulatorio(
    texto_regulacion: str,
    contexto_servicios: list[str]
) -> dict:
    """
    Analiza un cambio regulatorio y evalúa su impacto
    en la oferta de consultoría.
    """
    mensaje = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": f"""Analiza el siguiente cambio regulatorio
            y evalúa su impacto para una consultora tecnológica
            que ofrece estos servicios: {contexto_servicios}

            Texto del cambio regulatorio:
            {texto_regulacion}

            Estructura tu análisis en:
            1. RESUMEN: qué cambia y a quién afecta (3-5 frases)
            2. PLAZOS: fechas de cumplimiento obligatorio
            3. SECTORES AFECTADOS: qué industrias deben actuar
            4. SERVICIOS DEMANDADOS: qué necesitarán los clientes
               (assessment, gap analysis, auditoría, formación,
               implementación técnica)
            5. VENTANA DE OPORTUNIDAD: cuánto tiempo antes de que
               el mercado se sature
            6. COMPETIDORES POSICIONADOS: quién ya ofrece servicios
               relacionados (basado en información pública conocida)
            7. RECOMENDACIÓN: qué debemos hacer y cuándo

            Sé específico con plazos y datos. Si no tienes información
            suficiente para un apartado, indícalo explícitamente."""
        }]
    )

    return _parsear_analisis_regulatorio(mensaje.content[0].text)
