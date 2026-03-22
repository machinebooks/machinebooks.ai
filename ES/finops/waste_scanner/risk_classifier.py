# Extraído de: LibroFinOps/cap-15-waste-automatico.md
# waste_scanner/risk_classifier.py
import anthropic
import json

client = anthropic.Anthropic()

WASTE_CLASSIFIER_PROMPT = """Eres un experto en seguridad operativa y FinOps cloud.
Tu función es clasificar el riesgo de eliminar recursos cloud potencialmente huérfanos.

Para cada recurso, evalúa el riesgo de borrado considerando:
- Antigüedad: recursos más antiguos son más seguros de borrar
- Etiquetas: etiquetas de 'prod' o 'production' aumentan el riesgo
- Nombre: nombres que sugieren criticidad aumentan el riesgo
- Último acceso: acceso reciente aumenta el riesgo
- Tipo de recurso: los load balancers vacíos son casi siempre seguros de eliminar

Principio de precaución: ante la duda, clasifica como riesgo ALTO.
El ahorro de borrar un recurso nunca justifica perder datos críticos.

Para cada recurso, responde con:
{
  "resource_id": "...",
  "risk_level": "low|medium|high",
  "risk_reasons": ["razón 1", "razón 2"],
  "recommendation": "Una frase: borrar|investigar|mantener",
  "notes": "Contexto adicional si aplica"
}"""


def classify_waste_risk(resources: list[dict]) -> list[dict]:
    """
    Clasifica el riesgo de eliminar cada recurso huérfano.
    Agrupa en un único prompt para minimizar coste de tokens.
    """
    user_message = f"""Clasifica el riesgo de eliminar estos recursos huérfanos:

{json.dumps(resources, indent=2, default=str)}

Devuelve un array JSON con un objeto de clasificación por recurso."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=WASTE_CLASSIFIER_PROMPT,
        messages=[{"role": "user", "content": user_message}]
    )

    try:
        classifications = json.loads(response.content[0].text)
        if isinstance(classifications, dict):
            classifications = [classifications]
        return classifications
    except json.JSONDecodeError:
        # Si falla el parsing, todos los recursos pasan a riesgo alto por seguridad
        return [
            {'resource_id': r['resource_id'], 'risk_level': 'high',
             'risk_reasons': ['Error en clasificación automática'],
             'recommendation': 'investigar'}
            for r in resources
        ]
