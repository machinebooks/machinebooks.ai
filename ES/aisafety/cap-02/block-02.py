# Extraido de: LibroAISafety/cap-02-model-cards.md
# Estructura para un dataset de evaluación de seguridad propio
from dataclasses import dataclass, field

@dataclass
class TestCase:
    """Un caso de prueba de seguridad contextualizado."""
    id: str
    categoria: str           # "jailbreak", "exfiltracion", "inyeccion"
    prompt: str              # El prompt adversarial
    contexto: str            # System prompt + datos RAG simulados
    resultado_esperado: str  # "rechazo", "respuesta_segura"
    severidad: str           # "low", "medium", "high", "critical"
    tecnica: str             # "many-shot", "role-play", "encoding"
    idioma: str              # Importante: evaluar en todos los idiomas de despliegue

@dataclass
class EvaluacionSeguridad:
    """Resultado de una evaluación de seguridad propia."""
    modelo: str
    version: str
    fecha: str
    total_tests: int
    fallos: int
    tasa_rechazo: float      # Porcentaje de rechazos correctos
    falsos_positivos: int    # Rechazos incorrectos (sobrerechazo)
    tests_por_categoria: dict = field(default_factory=dict)
    tests_por_idioma: dict = field(default_factory=dict)
