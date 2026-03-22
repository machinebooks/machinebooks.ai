# Extraído de: LibroConsultor/cap-16-roadmaps-ia.md
def recomendar_tipo_adquisicion(
    iniciativa: dict,
    contexto_cliente: dict
) -> TipoAdquisicion:
    """Recomienda build/buy/integrate según criterios del cliente."""
    es_diferencial = iniciativa.get("diferenciacion_negocio", False)
    tiene_equipo = contexto_cliente.get("equipo_ml_interno", 0) >= 3
    datos_propios = iniciativa.get("requiere_datos_propios", False)
    urgencia_alta = iniciativa.get("time_to_value_dias", 180) < 90
    presupuesto_limitado = contexto_cliente.get("restriccion_presupuesto", False)
    regulacion_estricta = contexto_cliente.get("sector_regulado", False)

    # Regla 1: si es diferencial y hay equipo, construir
    if es_diferencial and tiene_equipo and datos_propios:
        return TipoAdquisicion.BUILD

    # Regla 2: si hay urgencia o presupuesto limitado, integrar API
    if urgencia_alta or (presupuesto_limitado and not es_diferencial):
        return TipoAdquisicion.INTEGRATE

    # Regla 3: si regulación exige control de datos, build o buy on-premise
    if regulacion_estricta and datos_propios:
        return TipoAdquisicion.BUILD if tiene_equipo else TipoAdquisicion.BUY

    # Regla 4: por defecto, comprar si existe solución madura
    if iniciativa.get("soluciones_mercado_maduras", 0) >= 3:
        return TipoAdquisicion.BUY

    # Regla 5: integrar como fallback
    return TipoAdquisicion.INTEGRATE
