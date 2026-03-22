# Extraído de: LibroConsultor/cap-20-pricing.md
@tool
def calcular_breakeven_retainer(
    coste_mensual_automatizacion: float,
    coste_mensual_equipo_dedicado: float,
    precio_retainer_mensual: float,
    horas_consultor_incluidas: int
) -> str:
    """Calcula el punto de equilibrio para un modelo de retainer.

    Args:
        coste_mensual_automatizacion: Coste mensual de infraestructura IA
        coste_mensual_equipo_dedicado: Coste del equipo asignado (parcial)
        precio_retainer_mensual: Precio del retainer al cliente
        horas_consultor_incluidas: Horas de consultor senior incluidas/mes
    """
    coste_hora_senior = 195.0  # Coste cargado
    coste_horas = horas_consultor_incluidas * coste_hora_senior
    coste_total_mensual = (
        coste_mensual_automatizacion + coste_mensual_equipo_dedicado + coste_horas
    )
    margen_por_cliente = precio_retainer_mensual - coste_total_mensual

    # Costes fijos de la infraestructura de retainer
    costes_fijos_mensuales = 4200  # Plataforma, monitorización, mantenimiento

    if margen_por_cliente <= 0:
        return json.dumps({
            "viable": False,
            "mensaje": "El retainer no cubre costes variables por cliente"
        })

    clientes_breakeven = costes_fijos_mensuales / margen_por_cliente

    return json.dumps({
        "viable": True,
        "coste_por_cliente_mes": f"€{coste_total_mensual:,.0f}",
        "margen_por_cliente_mes": f"€{margen_por_cliente:,.0f}",
        "clientes_breakeven": round(clientes_breakeven, 1),
        "margen_con_15_clientes": f"€{(margen_por_cliente * 15 - costes_fijos_mensuales):,.0f}/mes",
        "arr_con_15_clientes": f"€{precio_retainer_mensual * 15 * 12:,.0f}",
    }, indent=2, ensure_ascii=False)
