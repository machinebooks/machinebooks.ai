# Extraído de: LibroConsultor/cap-10-estimacion-esfuerzos.md
from dataclasses import dataclass
import statistics

@dataclass
class EstimacionCalibrada:
    horas_base: float            # estimación del consultor
    horas_calibrada: float       # ajustada por sesgo histórico
    intervalo_p10: float         # percentil 10 (optimista)
    intervalo_p50: float         # percentil 50 (más probable)
    intervalo_p90: float         # percentil 90 (pesimista)
    confianza: str               # "alta", "media", "baja"
    n_proyectos_referencia: int
    ratio_desviacion_medio: float
    factores_riesgo: list[str]

def calibrar_estimacion(
    horas_base: float,
    proyectos_referencia: list[ProyectoHistorico],
    nivel_confianza: float = 0.80
) -> EstimacionCalibrada:
    """
    Calibra la estimación base usando desviaciones históricas.

    Lógica: si los proyectos similares se desviaron un 35% de media,
    la estimación base se ajusta un 35% al alza. Los percentiles
    se calculan a partir de la distribución real de desviaciones.
    """
    if len(proyectos_referencia) < 3:
        confianza = "baja"
    elif len(proyectos_referencia) < 7:
        confianza = "media"
    else:
        confianza = "alta"

    # Extraer ratios de desviación reales
    ratios = [p.ratio_desviacion for p in proyectos_referencia]

    ratio_medio = statistics.mean(ratios)
    ratio_mediana = statistics.median(ratios)

    # Ajustar la estimación base por el sesgo histórico
    # Usamos la mediana (más resistente a outliers que la media)
    horas_calibrada = horas_base * ratio_mediana

    # Calcular percentiles para el intervalo de confianza
    ratios_ordenados = sorted(ratios)
    n = len(ratios_ordenados)

    def percentil(datos, p):
        k = (len(datos) - 1) * p / 100
        f = int(k)
        c = f + 1 if f + 1 < len(datos) else f
        d = k - f
        return datos[f] + d * (datos[c] - datos[f])

    p10 = horas_base * percentil(ratios_ordenados, 10)
    p50 = horas_base * percentil(ratios_ordenados, 50)
    p90 = horas_base * percentil(ratios_ordenados, 90)

    # Identificar factores de riesgo de proyectos que se desviaron más
    factores = []
    for p in proyectos_referencia:
        if p.ratio_desviacion > 1.3 and p.factores_desviacion:
            factores.append(
                f"{p.nombre}: {p.factores_desviacion}"
            )

    return EstimacionCalibrada(
        horas_base=horas_base,
        horas_calibrada=round(horas_calibrada, 0),
        intervalo_p10=round(p10, 0),
        intervalo_p50=round(p50, 0),
        intervalo_p90=round(p90, 0),
        confianza=confianza,
        n_proyectos_referencia=n,
        ratio_desviacion_medio=round(ratio_medio, 2),
        factores_riesgo=factores
    )
