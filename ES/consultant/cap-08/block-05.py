# Extraído de: LibroConsultor/cap-08-analisis-rfps.md
PROMPT_CONTRADICCIONES = """Analiza el siguiente RFP buscando
contradicciones internas entre secciones.

Tipos de contradicción a buscar:
1. Plazos o fechas inconsistentes entre secciones
2. Importes o penalizaciones que difieren
3. Requisitos de experiencia o perfil con valores distintos
4. Criterios de valoración que suman más o menos de 100
5. Obligaciones contradictorias (ej: "máximo 3 perfiles" vs
   "el equipo mínimo incluirá 5 personas")

Para cada contradicción encontrada indica:
- Elemento contradictorio
- Versión A: texto y página
- Versión B: texto y página
- Severidad: alta (puede causar exclusión), media (puede causar
  reclamación), baja (ambigüedad menor)
- Recomendación: si pedir aclaración formal o interpretar
  conservadoramente

Si no encuentras contradicciones, indícalo explícitamente."""

def detectar_contradicciones(texto_rfp: str) -> dict:
    """Busca contradicciones internas en el RFP."""
    mensaje = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=3000,
        system="Eres un analista legal especializado en pliegos "
               "de licitación. Tu función es detectar inconsistencias "
               "internas que puedan generar riesgo contractual.",
        messages=[{
            "role": "user",
            "content": f"{PROMPT_CONTRADICCIONES}\n\n"
                       f"TEXTO:\n{texto_rfp}"
        }]
    )
    return {
        "contradicciones": mensaje.content[0].text,
        "tokens": mensaje.usage.input_tokens + mensaje.usage.output_tokens
    }
