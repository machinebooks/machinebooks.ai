# Extraído de: LibroConsultor/cap-10-estimacion-esfuerzos.md
def cerrar_proyecto_y_actualizar(
    proyecto_id: str,
    horas_reales: float,
    duracion_real: int,
    equipo_real: int,
    factores_desviacion: str | None = None
) -> dict:
    """
    Al cerrar un proyecto, actualiza la base histórica
    y recalcula las métricas de calibración.
    """
    proyecto = obtener_proyecto(proyecto_id)

    # Actualizar datos reales
    proyecto.horas_reales = horas_reales
    proyecto.duracion_semanas_real = duracion_real
    proyecto.equipo_real = equipo_real
    proyecto.ratio_desviacion = horas_reales / proyecto.horas_estimadas
    proyecto.factores_desviacion = factores_desviacion

    guardar_proyecto(proyecto)

    # Recalcular métricas globales de calibración
    todos = obtener_todos_proyectos()
    ratios = [p.ratio_desviacion for p in todos if p.horas_reales > 0]

    metricas = {
        "n_proyectos": len(ratios),
        "ratio_medio": round(statistics.mean(ratios), 2),
        "ratio_mediano": round(statistics.median(ratios), 2),
        "mejora_ultimo_anio": calcular_tendencia(todos),
    }

    return metricas
