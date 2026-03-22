# Extraído de: LibroCISO/cap-11-rag-normativo.md
# Ejemplo didáctico: el RAG normativo como herramienta de agente
from anthropic import Anthropic

# Definición de la herramienta RAG para agentes Claude
rag_tool = {
    "name": "search_regulation",
    "description": (
        "Busca en el corpus normativo indexado (RGPD, LOPDGDD, ENS, "
        "guías AEPD, CCN-STIC, NIS2, DORA, AI Act). "
        "Usa esta herramienta SIEMPRE que necesites citar un artículo, "
        "verificar un requisito o fundamentar una recomendación regulatoria."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Pregunta sobre regulación en lenguaje natural",
            },
            "regulation": {
                "type": "string",
                "enum": ["RGPD", "LOPDGDD", "ENS", "NIS2", "DORA", "AI_ACT"],
                "description": "Filtro opcional por regulación específica",
            },
        },
        "required": ["query"],
    },
}

# El agente usa la herramienta como parte de su flujo de análisis
client = Anthropic()
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=4096,
    system="Eres un agente de privacidad. Usa search_regulation para "
           "fundamentar tus análisis con citas normativas verificables.",
    tools=[rag_tool],
    messages=[{
        "role": "user",
        "content": "Analiza si el tratamiento de datos biométricos "
                   "para control de acceso requiere DPIA."
    }],
)
