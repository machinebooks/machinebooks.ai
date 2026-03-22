# Extraído de: LibroConsultor/cap-10-estimacion-esfuerzos.md
FACTORES_RIESGO = {
    "cliente_nuevo": 1.15,        # +15%: sin historial previo
    "equipo_junior": 1.20,        # +20%: >40% del equipo junior
    "tecnologia_nueva": 1.25,     # +25%: tecnología no usada antes
    "multi_framework": 1.10,      # +10%: más de un framework normativo
    "dependencia_tercero": 1.15,  # +15%: dependencia externa
    "alcance_difuso": 1.30,       # +30%: requisitos no cerrados
    "plazo_agresivo": 1.10,       # +10%: duración < 70% de la media
    "distribucion_geografica": 1.10,  # +10%: >2 sedes del cliente
}

def aplicar_factores_riesgo(
    estimacion: EstimacionCalibrada,
    factores_activos: list[str]
) -> EstimacionCalibrada:
    """Ajusta la estimación calibrada con factores de riesgo adicionales."""
    multiplicador = 1.0
    for factor in factores_activos:
        if factor in FACTORES_RIESGO:
            multiplicador *= FACTORES_RIESGO[factor]

    # Aplicar multiplicador compuesto (limitado a 2.0x para evitar
    # estimaciones absurdas con muchos factores acumulados)
    multiplicador = min(multiplicador, 2.0)

    return EstimacionCalibrada(
        horas_base=estimacion.horas_base,
        horas_calibrada=round(
            estimacion.horas_calibrada * multiplicador, 0
        ),
        intervalo_p10=round(estimacion.intervalo_p10 * multiplicador, 0),
        intervalo_p50=round(estimacion.intervalo_p50 * multiplicador, 0),
        intervalo_p90=round(estimacion.intervalo_p90 * multiplicador, 0),
        confianza=estimacion.confianza,
        n_proyectos_referencia=estimacion.n_proyectos_referencia,
        ratio_desviacion_medio=round(
            estimacion.ratio_desviacion_medio * multiplicador, 2
        ),
        factores_riesgo=estimacion.factores_riesgo + factores_activos
    )
