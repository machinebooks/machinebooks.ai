# Extraído de: LibroTecnico/cap-23-inteligencia-comercial.md
class HeatmapEngine:
    """
    Motor de cálculo del scoring multidimensional.
    Los pesos de cada dimensión son configurables desde el panel Admin
    y se cargan desde la tabla HeatmapConfig en cada ejecución.
    """

    def __init__(self, period: str):
        self.period = period
        # Pesos configurables — no hardcodeados en el motor
        config = HeatmapConfig.query.filter_by(active=True).first()
        self.weights = {
            'demand':       config.weight_demand / 100,       # default 0.30
            'traction':     config.weight_traction / 100,     # default 0.20
            'economic':     config.weight_economic / 100,     # default 0.25
            'right_to_win': config.weight_right_to_win / 100  # default 0.25
        }

    def compute_for_cell(self, sector_id: int, service_line_id: int) -> dict:
        """
        Calcula el score para una celda específica de la matriz.
        Retorna el score total y los subscores por dimensión.
        """
        demand_data = self._get_demand_data(sector_id, service_line_id)
        traction_data = self._get_traction_data(sector_id, service_line_id)
        economic_data = self._get_economic_data(sector_id, service_line_id)
        rtw_data = self._get_rtw_data(sector_id, service_line_id)

        # Normalizar cada subscore al rango 0-100
        score_demand = self._normalize(demand_data['opportunity_value'],
                                       self.demand_p10, self.demand_p90)
        score_traction = self._normalize(traction_data['pipeline_volume'],
                                         self.traction_p10, self.traction_p90)
        score_economic = self._compute_economic_score(economic_data)
        score_rtw = self._compute_rtw_score(rtw_data)

        total = (
            score_demand * self.weights['demand'] +
            score_traction * self.weights['traction'] +
            score_economic * self.weights['economic'] +
            score_rtw * self.weights['right_to_win']
        ) * 100

        return {
            'total_score': round(total, 1),
            'score_demand': round(score_demand * 100, 1),
            'score_traction': round(score_traction * 100, 1),
            'score_economic': round(score_economic * 100, 1),
            'score_right_to_win': round(score_rtw * 100, 1),
            # Datos raw para auditabilidad
            'opportunities_count': demand_data['count'],
            'pipeline_volume': traction_data['pipeline_volume'],
            'avg_margin_pct': economic_data['avg_margin'],
            'win_rate_pct': rtw_data['win_rate']
        }

    def _normalize(self, value: float, p10: float, p90: float) -> float:
        """
        Normalización robusta usando percentiles P10-P90 del período.
        Evita que outliers distorsionen el rango completo.
        """
        if p90 == p10:
            return 0.5  # Sin varianza: valor neutro
        normalized = (value - p10) / (p90 - p10)
        return max(0.0, min(1.0, normalized))  # Clamp [0, 1]
