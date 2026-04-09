# Extraido de: LibroAISafety/cap-11-red-teaming.md
# Generación de métricas agregadas del engagement
# Para el informe ejecutivo, no técnico

def generar_metricas(intentos: list[RedTeamAttempt]) -> dict:
    """Calcula métricas agregadas para el informe."""
    total = len(intentos)
    if total == 0:
        return {"error": "Sin intentos registrados"}

    exitos = sum(1 for i in intentos
                 if i.classification == ResultClassification.SUCCESS)
    parciales = sum(1 for i in intentos
                    if i.classification == ResultClassification.PARTIAL)

    # Desglose por categoría
    por_categoria = {}
    for cat in AttackCategory:
        cat_intentos = [i for i in intentos if i.category == cat]
        cat_exitos = [i for i in cat_intentos
                      if i.classification == ResultClassification.SUCCESS]
        if cat_intentos:
            por_categoria[cat.value] = {
                "intentos": len(cat_intentos),
                "exitos": len(cat_exitos),
                "tasa": round(len(cat_exitos) / len(cat_intentos), 3),
            }

    return {
        "total_intentos": total,
        "exitos": exitos,
        "parciales": parciales,
        "tasa_exito_global": round(exitos / total, 3),
        "por_categoria": por_categoria,
    }
