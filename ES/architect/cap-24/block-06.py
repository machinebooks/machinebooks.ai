# Extraído de: LibroTecnico/cap-24-documentacion-ia.md
def generar_evaluacion_impacto_privacidad(
    componente: str,
    datos_procesados: List[str],
    base_legal: str,
    controles_implementados: List[dict],
    riesgos_identificados: List[dict]
) -> str:
    """
    Genera el borrador de una evaluación de impacto en privacidad (DPIA)
    para un componente de IA que procesa datos personales.
    Requiere revisión obligatoria por el responsable de privacidad antes de publicar.
    """
    client = anthropic.Anthropic()

    contexto = {
        "componente": componente,
        "datos_procesados": datos_procesados,
        "base_legal": base_legal,
        "controles": controles_implementados,
        "riesgos_previos": riesgos_identificados
    }

    prompt = f"""Genera el borrador de una Evaluación de Impacto en Privacidad (DPIA)
para el componente de IA '{componente}'.

Contexto técnico del componente:
{json.dumps(contexto, ensure_ascii=False, indent=2)}

La evaluación debe seguir la estructura del RGPD (Artículo 35):
1. Descripción sistemática del tratamiento y sus fines
2. Evaluación de la necesidad y proporcionalidad
3. Evaluación de riesgos para los derechos y libertades de los interesados
4. Medidas para afrontar los riesgos, incluidas garantías y mecanismos de seguridad
5. Conclusión sobre el nivel de riesgo residual

IMPORTANTE: Este es un borrador para revisión jurídica y técnica.
Marcar con [REVISAR] cualquier afirmación que requiera confirmación legal.
No incluir lenguaje definitivo sobre cumplimiento normativo sin revisión experta."""

    mensaje = client.messages.create(
        model="claude-opus-4-6",  # Máxima capacidad para documentos de compliance
        max_tokens=6144,
        messages=[{"role": "user", "content": prompt}]
    )

    return mensaje.content[0].text
