# Extraído de: LibroFinOps/cap-23-coste-equipo.md
# services/tco_analyst.py
# Agente que analiza el TCO y genera recomendaciones en lenguaje natural.

import anthropic
from decimal import Decimal
from services.tco_calculator import DesgloseTCO


class TCOAnalyst:
    """
    Usa Claude para analizar un desglose de TCO y generar recomendaciones.
    """

    def __init__(self):
        self.client = anthropic.Anthropic()

    def analizar_tco(self, desglose: DesgloseTCO) -> str:
        """
        Genera un análisis del TCO con recomendaciones de optimización.

        Usa claude-haiku-4-5 porque el análisis de costes es una tarea
        de resumen estructurado, no de razonamiento complejo.
        Coste estimado por análisis: ~€0.003
        """
        contexto = f"""
Analiza el siguiente desglose de TCO de una plataforma con IA:

Proyecto: {desglose.proyecto_codigo}
Período: {desglose.mes_inicio} → {desglose.mes_fin}

COSTES:
- Personas: €{desglose.coste_personas_eur:.2f} ({desglose.porcentaje_personas:.1f}%)
- Tokens/IA: €{desglose.coste_tokens_eur:.2f}
- Cloud: €{desglose.coste_cloud_eur:.2f}
- Herramientas: €{desglose.coste_herramientas_eur:.2f}
- TOTAL: €{desglose.coste_total:.2f}

Ratio personas/IA: {desglose.ratio_personas_vs_ia:.1f}x

Desglose por perfil:
{chr(10).join(f"- {k}: €{float(v):.2f}" for k, v in desglose.desglose_por_perfil.items())}

Genera:
1. Una observación principal sobre la distribución de costes (2-3 frases)
2. El mayor riesgo financiero identificado (1-2 frases)
3. La oportunidad de optimización más impactante (1-2 frases)
Responde en español, sin jerga, orientado a decisiones de negocio.
"""
        message = self.client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=512,
            messages=[{"role": "user", "content": contexto}]
        )

        return message.content[0].text
