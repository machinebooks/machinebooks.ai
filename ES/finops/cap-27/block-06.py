# Extraído de: LibroFinOps/cap-27-caso-pricing-saas.md
# Datos del resultado del pricing v3 (primeros 6 meses)
RESULTADOS_PRICING_V3 = {
    "clientes": 23,
    "mrr_eur": 8_450,        # Monthly Recurring Revenue
    "arr_proyectado_eur": 101_400,

    # Distribución por tier
    "starter_clientes": 8,   # 8 clientes × €175/mes = €1.400
    "professional_clientes": 10, # 10 clientes × €375/mes = €3.750
    "business_clientes": 4,  # 4 clientes × €650/mes = €2.600
    "enterprise_clientes": 1, # 1 cliente × €700/mes negociado = €700

    # Márgenes reales (vs proyectados)
    "margen_contribucion_real_pct": 61.3,  # Proyectado: 65%
    "clientes_con_alerta_fair_use": 3,     # 13% del total
    "clientes_en_overage": 1,             # 4.3%: propuesto upgrade

    # Lecciones
    "clientes_perdidos_por_precio": 1,    # Percibió el precio como alto
    "clientes_ganados_vs_v2": 4,          # Más cierres por predictibilidad
}

# Comparación con iteraciones anteriores
COMPARACION_ITERACIONES = {
    "v1": {
        "clientes_mes_6": 12,
        "mrr_eur": 4_200,
        "margen_contribucion_estimado_pct": 58,
        "clientes_no_rentables": 2,
        "precio_promedio_usuario_mes": 14.7,
    },
    "v2": {
        "clientes_mes_6": 9,  # Pérdida por incertidumbre de pricing
        "mrr_eur": 3_800,
        "margen_contribucion_pct": 67,  # Mejor margen, menos clientes
        "clientes_no_rentables": 0,
        "precio_promedio_usuario_mes": "variable",
    },
    "v3": {
        "clientes_mes_6": 23,
        "mrr_eur": 8_450,
        "margen_contribucion_pct": 61.3,
        "clientes_no_rentables": 0,
        "precio_promedio_usuario_mes": 15.3,
    },
}
