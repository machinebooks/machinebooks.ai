# Extraído de: LibroFinOps/cap-16-forecasting.md
# forecasting/token_forecaster.py
from models.llm_usage_log import LLMUsageLog


class TokenCostForecaster:
    """
    Forecast de coste de tokens LLM. Usa el número de usuarios
    activos y el consumo medio por usuario como regresores,
    en lugar de la simple tendencia temporal.
    """

    def forecast_token_cost(self, target_month: str) -> dict:
        # Usuarios activos del último mes y tendencia
        active_users = self._get_active_users_trend(months_back=3)
        avg_cost_per_user = self._get_avg_cost_per_user(months_back=3)

        # Proyección: usuarios proyectados * coste medio proyectado
        projected_users = active_users['projected']
        projected_cost_per_user = avg_cost_per_user['projected']
        base_forecast = projected_users * projected_cost_per_user

        # Ajuste por cambios de precio del modelo (si los hay)
        price_adjustment = self._get_price_change_factor()

        return {
            'base_forecast_usd': round(base_forecast, 2),
            'price_adjusted_usd': round(
                base_forecast * price_adjustment, 2
            ),
            'projected_active_users': projected_users,
            'projected_cost_per_user_usd': round(
                projected_cost_per_user, 2
            ),
            'price_change_factor': price_adjustment,
            'model_mix': self._get_projected_model_mix()
        }
