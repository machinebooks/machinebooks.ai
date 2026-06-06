# Extraído de: LibroAIGateway/cap-05-router-smart-select.md
# Patrones que indican tarea compleja
_COMPLEX_PATTERNS = re.compile(
    r"\b(analiza[rd]?|analyz[ae]|compar[ae]|evalú[ae]|evaluat|implement[ae]?|"
    r"refactor|architec[a-z]*|review|audit|generat|diseña|"
    r"explica en detalle|comprehensive|investiga[r]?|investigat|"
    r"desarrolla[r]?|develop|optimize|optim[iza]+|debugg?)\b",
    re.IGNORECASE,
)

# Patrones de preguntas factuales cortas
_SIMPLE_PATTERNS = re.compile(
    r"^(qué es|cuál es|cuándo |cómo se llama|quién es|dónde está|"
    r"what is|who is|when is|how many|cuánto[s]?|dame un ejemplo|"
    r"define |traduc|hola|hello|hi |gracias|thanks|ok )",
    re.IGNORECASE,
)
