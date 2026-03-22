# Extraído de: LibroCyberrange/cap-07-redes-aislamiento.md
# Ejemplo didáctico: Generación de topología con Claude API

import anthropic

client = anthropic.Anthropic()

def generate_topology(description: str,
                      available_templates: list) -> dict:
    """Generar topología de red a partir de descripción textual."""
    prompt = f"""Genera una topología de red para un ejercicio
de ciberseguridad basada en esta descripción:

{description}

Templates de VM disponibles:
{json.dumps(available_templates, indent=2)}

Responde en JSON con este formato:
{{
  "networks": [
    {{"name": "DMZ", "subnet": "10.X.1.0/24", "type": "vlan"}},
    ...
  ],
  "nodes": [
    {{"name": "WebServer", "template": "ubuntu-22.04",
      "networks": ["DMZ"]}},
    ...
  ],
  "edges": [
    {{"from": "WebServer", "to": "DMZ"}},
    ...
  ]
}}

Criterios:
- Segmentar por función (DMZ, interna, gestión)
- El servidor web NUNCA en la misma red que el DC
- Incluir al menos un punto de pivote entre redes
- Ser realista: reflejar una empresa típica"""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    return json.loads(message.content[0].text)
