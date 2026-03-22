# Extraído de: LibroConsultor/cap-20-pricing.md
# Tarifas y costes base (escalados, no valores reales)
COSTE_HORA_CARGADO = 175.0      # Coste empresa por hora de consultor
COSTE_IA_POR_HORA = 3.50        # Tokens + infra por hora de proyecto IA
MARGEN_OBJETIVO_COST_PLUS = 0.38
PORCENTAJE_VALOR_CLIENTE = 0.12  # 12% del valor identificado
FEE_FIJO_RATIO = 0.75           # Proporción fija del híbrido
BONUS_RATIO = 0.08              # 8% del ahorro demostrable

def calcular_pricing(proyecto: ProyectoInput) -> PricingResult:
    """Calcula pricing bajo los cuatro modelos."""
    horas_con_ia = proyecto.horas_estimadas_sin_ia * proyecto.factor_reduccion_ia
    coste_equipo = horas_con_ia * COSTE_HORA_CARGADO
    coste_ia = horas_con_ia * COSTE_IA_POR_HORA
    coste_base = coste_equipo + coste_ia

    # Modelo 1: Cost-plus
    precio_cp = coste_base * (1 + MARGEN_OBJETIVO_COST_PLUS)
    margen_cp = (precio_cp - coste_base) / precio_cp

    # Modelo 2: Value-based
    precio_vb = proyecto.valor_cliente_estimado * PORCENTAJE_VALOR_CLIENTE
    precio_vb = max(precio_vb, coste_base * 1.15)  # Suelo: coste + 15%
    margen_vb = (precio_vb - coste_base) / precio_vb

    # Modelo 3: Hybrid (fee fijo + variable)
    fee_fijo = precio_cp * 1.15 * FEE_FIJO_RATIO  # Base 15% sobre cost-plus
    bonus_estimado = proyecto.valor_cliente_estimado * BONUS_RATIO * 0.6
    precio_hy = fee_fijo + bonus_estimado  # Estimación conservadora
    margen_hy = (precio_hy - coste_base) / precio_hy

    # Modelo 4: Retainer mensual (si aplica)
    precio_ret = (coste_base / 6) * 1.55 if proyecto.cliente_recurrente else 0
    margen_ret = 0.55 if proyecto.cliente_recurrente else 0

    # Lógica de recomendación
    if proyecto.es_licitacion_publica:
        recomendado = "cost_plus"
        justificacion = "Licitación pública: estructura rígida de oferta económica"
    elif proyecto.cliente_recurrente and proyecto.num_retainers_activos >= 10:
        recomendado = "retainer"
        justificacion = "Cliente recurrente con masa crítica de retainers"
    elif proyecto.valor_cliente_estimado > coste_base * 5:
        recomendado = "hybrid"
        justificacion = "Alto valor para el cliente, modelo híbrido captura upside"
    else:
        recomendado = "cost_plus"
        justificacion = "Relación valor/coste estándar, cost-plus es más seguro"

    return PricingResult(
        modelo_recomendado=recomendado,
        precio_cost_plus=round(precio_cp, 2),
        precio_value_based=round(precio_vb, 2),
        precio_hybrid=round(precio_hy, 2),
        precio_retainer_mensual=round(precio_ret, 2),
        margen_cost_plus=round(margen_cp, 4),
        margen_value_based=round(margen_vb, 4),
        margen_hybrid=round(margen_hy, 4),
        margen_retainer=round(margen_ret, 4),
        justificacion=justificacion,
        riesgos=_identificar_riesgos(proyecto, coste_base)
    )
