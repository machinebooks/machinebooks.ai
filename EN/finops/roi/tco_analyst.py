# Source: The FinOps Engineer and the Machine -- Chapter 23
# Pattern: AI-powered TCO analysis

# services/tco_analyst.py
# Agent that analyzes TCO and generates recommendations in natural language.

import anthropic
from decimal import Decimal
from services.tco_calculator import DesgloseTCO


class TCOAnalyst:
    """
    Uses Claude to analyze a TCO breakdown and generate recommendations.
    """

    def __init__(self):
        self.client = anthropic.Anthropic()

    def analizar_tco(self, desglose: DesgloseTCO) -> str:
        """
        Generates a TCO analysis with optimization recommendations.

        Uses claude-haiku-4-5 because cost analysis is a structured
        summarization task, not complex reasoning.
        Estimated cost per analysis: ~EUR0.003
        """
        contexto = f"""
Analyze the following TCO breakdown of an AI platform:

Project: {desglose.proyecto_codigo}
Period: {desglose.mes_inicio} -> {desglose.mes_fin}

COSTS:
- People: EUR{desglose.coste_personas_eur:.2f} ({desglose.porcentaje_personas:.1f}%)
- Tokens/AI: EUR{desglose.coste_tokens_eur:.2f}
- Cloud: EUR{desglose.coste_cloud_eur:.2f}
- Tools: EUR{desglose.coste_herramientas_eur:.2f}
- TOTAL: EUR{desglose.coste_total:.2f}

People/AI ratio: {desglose.ratio_personas_vs_ia:.1f}x

Breakdown by profile:
{chr(10).join(f"- {k}: EUR{float(v):.2f}" for k, v in desglose.desglose_por_perfil.items())}

Generate:
1. A main observation about the cost distribution (2-3 sentences)
2. The biggest financial risk identified (1-2 sentences)
3. The highest-impact optimization opportunity (1-2 sentences)
Respond in English, without jargon, oriented toward business decisions.
"""
        message = self.client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=512,
            messages=[{"role": "user", "content": contexto}]
        )

        return message.content[0].text
