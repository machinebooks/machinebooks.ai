# Extraído de: LibroConsultor/cap-11-inteligencia-competitiva.md
import anthropic
from datetime import datetime, timedelta

client = anthropic.Anthropic()

def generar_radar_tecnologico(
    dominios: list[str],
    periodo: str = "semanal"
) -> dict:
    """
    Genera un radar tecnológico basado en fuentes públicas:
    blogs técnicos, publicaciones regulatorias, conferencias.
    """
    fuentes_procesadas = []

    for dominio in dominios:
        # Recopilar artículos y publicaciones recientes
        articulos = _buscar_publicaciones_recientes(
            dominio, periodo
        )
        # Recopilar cambios regulatorios
        regulacion = _buscar_cambios_regulatorios(
            dominio, periodo
        )
        fuentes_procesadas.append({
            "dominio": dominio,
            "articulos": articulos,
            "regulacion": regulacion
        })

    # Análisis con Claude: cruzar fuentes y detectar tendencias
    mensaje = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": f"""Analiza las siguientes fuentes y genera un
            radar tecnológico estructurado.

            Fuentes: {fuentes_procesadas}

            Para cada tendencia identificada, indica:
            1. Nombre y descripción breve (2-3 frases)
            2. Nivel de madurez: emergente / en adopción / establecida
            3. Relevancia para consultoría tecnológica (alta/media/baja)
            4. Ventana de oportunidad estimada
            5. Competidores que ya se posicionan
            6. Fuentes que respaldan la señal

            Agrupa por: IA y automatización, cloud y infraestructura,
            seguridad y cumplimiento, datos y analítica.

            Solo incluye tendencias con al menos 2 fuentes
            independientes que las respalden."""
        }]
    )

    return _parsear_radar(mensaje.content[0].text)
