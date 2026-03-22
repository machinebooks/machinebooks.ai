# Extraído de: LibroConsultor/cap-20-pricing.md
def _identificar_riesgos(
    proyecto: ProyectoInput, coste_base: float
) -> list[str]:
    """Identifica riesgos comerciales del pricing propuesto."""
    riesgos = []

    # Riesgo de margen insuficiente
    if proyecto.horas_estimadas_sin_ia < 100:
        riesgos.append(
            "Proyecto pequeño: los costes fijos de gestión pueden erosionar el margen"
        )

    # Riesgo de scope creep en fee fijo
    if not proyecto.es_licitacion_publica and proyecto.tipo in ("roadmap", "assessment"):
        riesgos.append(
            "Alto riesgo de scope creep en fee fijo — definir entregables con precisión"
        )

    # Riesgo de variable no materializado
    if proyecto.valor_cliente_estimado > coste_base * 8:
        riesgos.append(
            "Componente variable depende de que el cliente implemente recomendaciones"
        )

    # Riesgo de competencia por precio
    if proyecto.sector == "publico" and not proyecto.es_licitacion_publica:
        riesgos.append(
            "Sector público sensible al precio — preparar argumentario de valor"
        )

    # Riesgo de percepción IA = descuento
    if proyecto.factor_reduccion_ia < 0.5:
        riesgos.append(
            "Reducción >50% por IA visible — preparar narrativa de valor, no de ahorro"
        )

    return riesgos
