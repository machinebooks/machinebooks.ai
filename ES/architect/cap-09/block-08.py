# Extraído de: LibroTecnico/cap-09-servicios-negocio.md
# Ejemplo didáctico: cálculo de score de relevancia para alertas
# Patrón: backend/tasks/alerts/opportunity_scorer.py

def calculate_opportunity_score(
    opportunity_id: int,
    area_portfolio: dict
) -> float:
    """
    Calcula el score de relevancia de una oportunidad para un área de negocio.
    Score 0-10; umbral por defecto 7.0 para generar alerta.
    """
    opportunity = Opportunity.query.get(opportunity_id)
    if not opportunity or not opportunity.embedding_vector:
        return 0.0

    # Señal 1: similitud semántica contra vector del portfolio del área
    semantic_score = calculate_vector_similarity(
        opportunity.embedding_vector,
        area_portfolio["portfolio_vector"]
    ) * 10  # Normalizar a escala 0-10

    # Señal 2: coincidencia de taxonomía (binaria)
    taxonomy_match = 1.0 if (
        opportunity.cpv_categories and
        set(opportunity.cpv_categories) & set(area_portfolio["cpv_codes"])
    ) else 0.0

    # Señal 3: win-rate histórico en categoría similar (0-10)
    win_rate_score = get_historical_win_rate(
        area_id=area_portfolio["area_id"],
        cpv_codes=opportunity.cpv_categories
    ) * 10

    # Ponderación: semántica 50%, taxonomía 30%, win-rate 20%
    final_score = (
        semantic_score * 0.5 +
        taxonomy_match * 10 * 0.3 +
        win_rate_score * 0.2
    )

    return round(min(final_score, 10.0), 2)
