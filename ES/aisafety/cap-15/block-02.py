# Extraido de: LibroAISafety/cap-15-sabotaje-riesgos.md
# Concepto de evaluación embebida en producción
# NO es un exploit — es una técnica defensiva de evaluación

from dataclasses import dataclass
import random

@dataclass
class EmbeddedEval:
    """Evaluación embebida en el flujo de producción."""
    eval_id: str
    real_request: str          # Petición real del usuario
    eval_variant: str          # Variante de evaluación
    expected_behavior: str     # Comportamiento esperado
    actual_behavior: str = ""  # Se rellena con la respuesta

def should_inject_eval(probability: float = 0.01) -> bool:
    """
    Decide si esta petición incluirá una evaluación embebida.
    Probabilidad baja para no afectar el rendimiento.
    """
    return random.random() < probability

def create_sabotage_eval(domain: str) -> EmbeddedEval:
    """
    Crea una evaluación de sabotaje específica del dominio.
    El modelo recibe una tarea real y se verifica
    si la respuesta contiene errores sutiles deliberados.
    """
    # La implementación depende del dominio
    # Para código: se envía código con un bug conocido
    #   y se verifica si el modelo lo detecta
    # Para datos: se envía un dataset con una anomalía
    #   y se verifica si el modelo la reporta
    pass
