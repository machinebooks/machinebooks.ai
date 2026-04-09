# Extraido de: LibroAISafety/cap-13-prompt-injection.md
# Cálculo del coste operativo de un clasificador de prompt injection
# Código didáctico para ilustrar el trade-off

def calcular_impacto_clasificador(
    peticiones_diarias: int,
    porcentaje_ataques: float,      # % de peticiones que son ataques
    tasa_deteccion: float,           # True positive rate
    tasa_falsos_positivos: float,    # False positive rate
) -> dict:
    """
    Calcula el impacto operativo de un clasificador de prompt injection.
    """
    ataques = int(peticiones_diarias * porcentaje_ataques)
    legitimas = peticiones_diarias - ataques

    ataques_bloqueados = int(ataques * tasa_deteccion)
    ataques_no_detectados = ataques - ataques_bloqueados
    legitimas_bloqueadas = int(legitimas * tasa_falsos_positivos)

    return {
        "ataques_bloqueados_dia": ataques_bloqueados,
        "ataques_que_pasan_dia": ataques_no_detectados,
        "peticiones_legitimas_bloqueadas_dia": legitimas_bloqueadas,
        "ratio_dano_colateral": round(
            legitimas_bloqueadas / max(ataques_bloqueados, 1), 2
        ),
    }

# Ejemplo: 10.000 peticiones/día, 0.5% son ataques
# Clasificador: 95% detección, 2% falsos positivos
resultado = calcular_impacto_clasificador(10000, 0.005, 0.95, 0.02)
# ataques_que_pasan_dia: 2-3
# peticiones_legitimas_bloqueadas_dia: ~199
# Por cada ataque bloqueado, ~4 peticiones legítimas bloqueadas
