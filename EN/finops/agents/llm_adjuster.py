# Source: The FinOps Engineer and the Machine -- Chapter 16
# Pattern: LLM-powered forecast adjustment with business context

# forecasting/llm_adjuster.py
import anthropic
import json
from datetime import date

client = anthropic.Anthropic()

FORECASTING_SYSTEM_PROMPT = """You are an expert FinOps analyst specialized in cloud
cost forecasting. You receive a statistical base projection and business context.

Your function is:
1. Evaluate whether the context justifies adjusting the statistical projection
2. Quantify adjustments with argumentation (do not invent numbers)
3. Produce a range: optimistic / expected / conservative
4. Explain in language a CFO can understand

PRINCIPLES:
- If the context does not justify an adjustment, keep the statistical base
- Adjustments are based on historical data or documented analogies
- Always produce a range, never a single number
- The explanation must be readable without cloud knowledge

Respond in JSON:
{
  "statistical_base_usd": ...,
  "adjusted_forecast_usd": ...,
  "range_low_usd": ...,
  "range_high_usd": ...,
  "confidence_level": "high|medium|low",
  "adjustments": [
    {"factor": "description", "impact_usd": ..., "reasoning": "..."}
  ],
  "executive_summary": "2-3 sentences for the CFO",
  "key_uncertainties": ["uncertainty 1", "uncertainty 2"]
}"""


def adjust_forecast_with_context(
    statistical_data: dict,
    business_context: str,
    historical_context: str
) -> dict:
    """
    Adjusts the statistical forecast with business context.
    Returns the forecast with range and executive explanation.
    """
    today = date.today()

    user_message = f"""Adjust this cloud cost forecast.

STATISTICAL BASE PROJECTION:
{json.dumps(statistical_data, indent=2)}

BUSINESS CONTEXT ({today.strftime('%B %Y')}):
{business_context}

HISTORICAL CONTEXT (similar periods):
{historical_context}

Produce the adjusted forecast with detailed justification."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=FORECASTING_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}]
    )

    try:
        return json.loads(response.content[0].text)
    except json.JSONDecodeError:
        # Fallback: statistical projection without LLM adjustment
        base = statistical_data.get('trend_adjusted_projection_usd')
        return {
            'statistical_base_usd': base,
            'adjusted_forecast_usd': base,
            'range_low_usd': base * 0.9,
            'range_high_usd': base * 1.1,
            'confidence_level': 'low',
            'adjustments': [],
            'executive_summary': 'Statistical forecast without contextual '
                                 'adjustment (LLM analysis error).',
            'key_uncertainties': [
                'LLM analysis error: use base projection'
            ]
        }
