# Extraido de: LibroAISafety/cap-02-model-cards.md
from dataclasses import dataclass
from datetime import date

@dataclass
class DiscrepanciaModelCard:
    """Registra una discrepancia entre lo que la Model Card
    afirma y lo que la evidencia externa demuestra."""
    modelo: str
    claim_model_card: str    # Afirmación de la Model Card
    evidencia_externa: str   # Paper, informe o prueba propia
    fuente: str              # URL o referencia del paper
    fecha_descubrimiento: date
    severidad: str           # "info", "warning", "critical"
    impacto_despliegue: str  # Cómo afecta a nuestro sistema

# Ejemplo real
discrepancia = DiscrepanciaModelCard(
    modelo="modelo-ejemplo-v2",
    claim_model_card="Tasa de rechazo de contenido dañino: 96,2%",
    evidencia_externa="Técnica many-shot con 256 ejemplos: "
                      "éxito del 38% en categorías restringidas",
    fuente="Anil et al., 2024 — Many-shot Jailbreaking",
    fecha_descubrimiento=date(2026, 3, 15),
    severidad="critical",
    impacto_despliegue="Nuestro sistema permite contextos largos "
                       "para análisis documental — superficie expuesta"
)
