# Extraído de: LibroConsultor/cap-08-analisis-rfps.md
@dataclass
class PerfilFirma:
    """Capacidades y experiencia de la práctica consultora."""
    certificaciones: list[str]
    # Ejemplo: ["ISO 27001", "ISO 9001", "ENS nivel medio"]
    experiencia_sectorial: dict[str, int]
    # Ejemplo: {"sector_publico_salud": 8, "banca": 12}
    proyectos_referencia: list[dict]
    # Cada uno: {sector, importe, duracion, año, descripcion}
    perfiles_disponibles: list[dict]
    # Cada uno: {rol, certificaciones, años_exp, disponibilidad}
    facturacion_media_anual: float
    clasificaciones_empresariales: list[str]

def cruzar_requisitos_capacidades(
    requisitos: list[dict],
    perfil: PerfilFirma
) -> list[dict]:
    """Cruza cada requisito obligatorio con las capacidades
    de la práctica y genera una evaluación de cumplimiento."""

    prompt_cruce = """Dados los siguientes requisitos obligatorios
de un RFP y el perfil de capacidades de la práctica consultora,
evalúa el cumplimiento de CADA requisito.

Para cada requisito indica:
- cumple: sí / no / parcial
- evidencia: qué dato del perfil demuestra el cumplimiento
- brecha: si no cumple, qué falta exactamente
- mitigación: si hay brecha, opciones para resolverla
  (UTE, subcontratación, obtención de certificación, etc.)
- riesgo_exclusión: alto / medio / bajo

REQUISITOS DEL RFP:
{requisitos}

PERFIL DE LA FIRMA:
{perfil}"""

    mensaje = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system="Eres un analista de preventa que evalúa el encaje "
               "entre requisitos de un RFP y capacidades de la práctica. "
               "Sé conservador: ante la duda, marca como 'parcial' "
               "y documenta la brecha.",
        messages=[{
            "role": "user",
            "content": prompt_cruce.format(
                requisitos=str(requisitos),
                perfil=str(perfil.__dict__)
            )
        }]
    )
    return mensaje.content[0].text
