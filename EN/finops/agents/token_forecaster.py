# Source: The FinOps Engineer and the Machine -- Chapter 16
# Pattern: Token-specific cost forecasting

# forecasting/token_forecaster.py
from models.llm_usage_log import LLMUsageLog


class TokenCostForecaster:
    """
    LLM token cost forecast. Uses the number of active
    users and average cost per user as regressors,
    instead of simple time trend.
    """

    def forecast_token_cost(self, target_month: str) -> dict:
        # Active users from last month and trend
        active_users = self._get_active_users_trend(months_back=3)
        avg_cost_per_user = self._get_avg_cost_per_user(months_back=3)

        # Projection: projected users * projected cost per user
        projected_users = active_users['projected']
        projected_cost_per_user = avg_cost_per_user['projected']
        base_forecast = projected_users * projected_cost_per_user

        # Adjustment for model price changes (if any)
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
