# Extraído de: LibroConsultor/cap-21-productizacion.md
@dataclass
class ProductizationCandidate:
    service_name: str
    repetition_score: float    # 0-1: ¿cuántas veces lo hemos hecho?
    variability_score: float   # 0-1: ¿cuánto cambia entre clientes?
    automation_potential: float # 0-1: ¿qué % del trabajo es mecánico?
    demand_signal: float       # 0-1: ¿lo piden los clientes espontáneamente?[^senal_demanda]

    @property
    def productization_score(self) -> float:
        """Índice de productización. >0.6 = candidato viable."""
        return (
            self.repetition_score * 0.30
            + (1 - self.variability_score) * 0.25  # Menos variabilidad = mejor
            + self.automation_potential * 0.25
            + self.demand_signal * 0.20
        )

# Evaluación de nuestros tres candidatos
candidates = [
    ProductizationCandidate(
        service_name="Assessment de madurez IA",
        repetition_score=0.9,     # 23 veces en 18 meses
        variability_score=0.3,    # Framework estable, adaptación menor
        automation_potential=0.75, # 38/60 horas automatizables
        demand_signal=0.8,        # Clientes lo piden proactivamente
    ),
    ProductizationCandidate(
        service_name="Auditoría de cumplimiento",
        repetition_score=0.85,
        variability_score=0.7,    # Alta: cambia mucho por marco normativo
        automation_potential=0.60,
        demand_signal=0.6,
    ),
    ProductizationCandidate(
        service_name="Monitorización continua",
        repetition_score=0.2,     # Baja: nunca lo hemos vendido como tal
        variability_score=0.5,
        automation_potential=0.85,
        demand_signal=0.9,        # Muy pedido pero no existía
    ),
]

for c in candidates:
    print(f"{c.service_name}: {c.productization_score:.2f}")
# Assessment de madurez IA: 0.77
# Auditoría de cumplimiento: 0.55
# Monitorización continua: 0.58
