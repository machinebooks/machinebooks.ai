# Source: The FinOps Engineer and the Machine -- Chapter 29
# Pattern: Jevons paradox monitor

# services/jevons_monitor.py
# Detects whether the Jevons paradox occurs: total spend rises
# despite improvements in unit efficiency.

from dataclasses import dataclass


@dataclass
class DiagnosticoJevons:
    """Diagnosis of whether the Jevons paradox is active."""
    activa: bool
    reduccion_coste_unitario_pct: float
    incremento_volumen_pct: float
    variacion_gasto_total_pct: float
    explicacion: str
    recomendacion: str


class JevonsMonitor:
    """
    The paradox is triggered when:
    1. Unit cost drops (due to technical optimizations)
    2. Volume grows more than proportionally
    3. Total spend rises despite the optimization

    The answer is not "optimize less": it is to align the growth
    strategy with total spend objectives.
    """

    def diagnosticar(
        self, coste_unitario_anterior: float, coste_unitario_actual: float,
        volumen_anterior: int, volumen_actual: int,
    ) -> DiagnosticoJevons:
        if coste_unitario_anterior == 0 or volumen_anterior == 0:
            return DiagnosticoJevons(
                False, 0, 0, 0,
                "Insufficient historical data",
                "Wait at least 2 periods for diagnosis",
            )

        reduccion = (coste_unitario_anterior - coste_unitario_actual) / \
                     coste_unitario_anterior * 100
        incremento = (volumen_actual - volumen_anterior) / volumen_anterior * 100
        gasto_ant = coste_unitario_anterior * volumen_anterior
        gasto_act = coste_unitario_actual * volumen_actual
        variacion = (gasto_act - gasto_ant) / gasto_ant * 100

        paradoja = (reduccion > 0) and (variacion > 0)

        if paradoja:
            return DiagnosticoJevons(
                activa=True,
                reduccion_coste_unitario_pct=round(reduccion, 1),
                incremento_volumen_pct=round(incremento, 1),
                variacion_gasto_total_pct=round(variacion, 1),
                explicacion=(
                    f"Paradox active: unit cost dropped {reduccion:.1f}% "
                    f"but volume grew {incremento:.1f}%, "
                    f"total spend +{variacion:.1f}%."
                ),
                recomendacion=(
                    "Evaluate whether the volume growth generates proportional "
                    "value. Consider adjusting pricing or introducing "
                    "fair use limits if it exceeds revenue forecasts."
                ),
            )
        return DiagnosticoJevons(
            False, round(reduccion, 1), round(incremento, 1),
            round(variacion, 1),
            f"No paradox: unit cost {reduccion:.1f}%, "
            f"volume {incremento:.1f}%, total spend {variacion:.1f}%.",
            "Evolution within expectations. Continue monitoring.",
        )
