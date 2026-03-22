# Extraído de: LibroTecnico/cap-10-automatizacion-rpa.md
# Ejemplo didáctico: patrones/automation/maintenance/diagnose_bot.py

import anthropic
from pathlib import Path

def generate_fix_with_claude(
    bot_code: str,
    error_message: str,
    current_html: str,
    screenshot_path: str | None = None
) -> str:
    """Usa Claude para generar una corrección cuando un bot falla por cambios de interfaz."""

    client = anthropic.Anthropic()

    prompt = (
        "Tengo un bot de Selenium que ha fallado con el siguiente error:\n\n"
        f"{error_message}\n\n"
        "El código del bot es:\n\n"
        f"{bot_code}\n\n"
        "El HTML actual de la página en el momento del fallo es:\n\n"
        f"{current_html[:3000]}\n\n"  # Limitado a 3000 chars para no exceder contexto
        "Necesito que:\n"
        "1. Identifiques el selector o elemento que ha cambiado\n"
        "2. Proporciones el código corregido con los nuevos selectores\n"
        "3. Revises si otros selectores del mismo flujo pueden haber cambiado también\n"
        "4. Expliques brevemente qué cambió para que pueda documentarlo\n\n"
        "Sé conciso y centra la respuesta en el código corregido."
    )

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        messages=[{"role": "user", "content": prompt}]
    )

    return message.content[0].text
