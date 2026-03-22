# Extraído de: LibroFinOps/cap-29-convergencia.md
# services/jevons_monitor.py
# Detecta si se produce la paradoja de Jevons: gasto total sube
# a pesar de mejoras en eficiencia unitaria.

from dataclasses import dataclass


@dataclass
class DiagnosticoJevons:
    """Diagnóstico de si la paradoja de Jevons está activa."""
    activa: bool
    reduccion_coste_unitario_pct: float
    incremento_volumen_pct: float
    variacion_gasto_total_pct: float
    explicacion: str
    recomendacion: str


class JevonsMonitor:
    """
    La paradoja se activa cuando:
    1. El coste unitario cae (por optimizaciones técnicas)
    2. El volumen crece más que proporcionalmente
    3. El gasto total sube a pesar de la optimización

    La respuesta no es "optimizar menos": es alinear la estrategia
    de crecimiento con los objetivos de gasto total.
    """

    def diagnosticar(
        self, coste_unitario_anterior: float, coste_unitario_actual: float,
        volumen_anterior: int, volumen_actual: int,
    ) -> DiagnosticoJevons:
        if coste_unitario_anterior == 0 or volumen_anterior == 0:
            return DiagnosticoJevons(
                False, 0, 0, 0,
                "Sin datos históricos suficientes",
                "Esperar al menos 2 períodos para diagnóstico",
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
                    f"Paradoja activa: coste unitario bajó {reduccion:.1f}% "
                    f"pero volumen creció {incremento:.1f}%, "
                    f"gasto total +{variacion:.1f}%."
                ),
                recomendacion=(
                    "Evaluar si el crecimiento de volumen genera valor "
                    "proporcional. Considerar ajustar pricing o introducir "
                    "límites de fair use si supera las previsiones de ingresos."
                ),
            )
        return DiagnosticoJevons(
            False, round(reduccion, 1), round(incremento, 1),
            round(variacion, 1),
            f"Sin paradoja: coste unitario {reduccion:.1f}%, "
            f"volumen {incremento:.1f}%, gasto total {variacion:.1f}%.",
            "Evolución dentro de lo esperado. Continuar monitorizando.",
        )
