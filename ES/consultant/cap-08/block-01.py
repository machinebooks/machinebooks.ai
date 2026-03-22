# Extraído de: LibroConsultor/cap-08-analisis-rfps.md
client = anthropic.Anthropic()

# Categorías de extracción con prompts especializados
CATEGORIAS_EXTRACCION = {
    "requisitos_obligatorios": {
        "descripcion": "Requisitos de solvencia, experiencia y capacidad "
                       "que son condición de admisión (no valoración)",
        "prompt": """Analiza el siguiente texto de un RFP/pliego y extrae
TODOS los requisitos obligatorios para la admisión de la oferta.

Incluye:
- Requisitos de solvencia técnica y económica
- Certificaciones obligatorias (ISO, ENS, etc.)
- Experiencia mínima exigida (años, proyectos, importes)
- Perfiles profesionales obligatorios con titulación o certificación
- Clasificación empresarial requerida
- Requisitos de UTE o subcontratación

Para cada requisito indica:
- Descripción exacta (cita textual cuando sea posible)
- Página donde aparece
- Si es eliminatorio o admite subsanación
- Nivel de certeza (alto/medio/bajo) sobre si es obligatorio

IMPORTANTE: Si un requisito aparece como "se valorará" no es
obligatorio. Si aparece como "deberá acreditar" o "es requisito
imprescindible", sí lo es. Ante la duda, clasifícalo como
obligatorio con certeza media."""
    },
    "criterios_valoracion": {
        "descripcion": "Criterios de puntuación técnica y económica "
                       "con pesos y subcriterios",
        "prompt": """Extrae los criterios de valoración de ofertas con:
- Nombre del criterio
- Peso (puntos o porcentaje sobre el total)
- Subcriterios si los hay, con su peso individual
- Si es evaluación automática (fórmula) o juicio de valor
- Página donde aparece
- Qué se pide exactamente para obtener puntuación máxima"""
    },
    "riesgos_penalizaciones": {
        "descripcion": "Penalizaciones, SLAs, garantías y cláusulas "
                       "de resolución contractual",
        "prompt": """Extrae todas las cláusulas de riesgo contractual:
- Penalizaciones por incumplimiento (importes o porcentajes)
- SLAs con umbrales y consecuencias
- Garantías exigidas (definitiva, complementaria)
- Causas de resolución del contrato
- Responsabilidades por daños
- Cláusulas de propiedad intelectual
- Obligaciones de transición al finalizar el contrato
- Página donde aparece cada cláusula"""
    },
    "plazos_calendario": {
        "descripcion": "Fechas, plazos de ejecución, hitos y "
                       "restricciones temporales",
        "prompt": """Extrae toda la información temporal del RFP:
- Plazo de presentación de ofertas
- Plazo de ejecución del contrato
- Hitos intermedios con fechas o plazos relativos
- Prórrogas posibles y condiciones
- Plazos de garantía post-entrega
- Restricciones de calendario (ventanas de mantenimiento,
  periodos de indisponibilidad)
- Página donde aparece cada dato temporal"""
    },
    "cumplimiento_normativo": {
        "descripcion": "Requisitos normativos, regulatorios y de "
                       "cumplimiento legal",
        "prompt": """Extrae los requisitos de cumplimiento normativo:
- Normativa aplicable citada (ENS, RGPD, NIS2, DORA, etc.)
- Nivel de cumplimiento exigido (categoría ENS, nivel RGPD)
- Certificaciones normativas requeridas vs valoradas
- Auditorías de cumplimiento durante la ejecución
- Requisitos de protección de datos (DPD, EIPD, etc.)
- Requisitos de soberanía digital o residencia de datos
- Página donde aparece cada requisito normativo"""
    }
}

def extraer_categoria(
    texto_rfp: str,
    categoria: str,
    config: dict
) -> dict:
    """Extrae una categoría de información del RFP."""
    mensaje = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system="""Eres un analista experto en licitaciones y RFPs.
Extraes información de forma precisa, citando páginas.
Si no encuentras información para una categoría, indícalo
explícitamente — nunca inventes datos.""",
        messages=[{
            "role": "user",
            "content": f"{config['prompt']}\n\n"
                       f"TEXTO DEL RFP:\n{texto_rfp}"
        }]
    )
    return {
        "categoria": categoria,
        "descripcion": config["descripcion"],
        "resultado": mensaje.content[0].text,
        "tokens_entrada": mensaje.usage.input_tokens,
        "tokens_salida": mensaje.usage.output_tokens
    }
