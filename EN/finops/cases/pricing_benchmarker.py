# Source: The FinOps Engineer and the Machine -- Chapter 27
# Pattern: Competitive pricing benchmarker

# services/pricing_benchmarker.py
# Pricing benchmarking against known market references.
# Uses Claude for qualitative positioning analysis.

import anthropic
from dataclasses import dataclass


@dataclass
class ReferenciaPricing:
    """Pricing reference data from a similar platform."""
    nombre: str          # Generic name (not a real identifier)
    tipo: str            # "plataforma-seguridad", "plataforma-pqc", etc.
    num_clientes: int
    precio_rango_eur: tuple[float, float]  # (min, max) per month
    usuarios_tipicos: int
    incluye_ia: bool
    notas: str


class PricingBenchmarker:
    """
    Compares own pricing structure with market references.
    """

    # Market references (data from the other platforms in the series)
    # Data is approximate and anonymized
    REFERENCIAS = [
        ReferenciaPricing(
            nombre="plataforma-seguridad-ofensiva",
            tipo="herramienta-especializada",
            num_clientes=20,
            precio_rango_eur=(580, 675),
            usuarios_tipicos=3,
            incluye_ia=True,
            notas="AI-powered audit platform for vulnerability analysis",
        ),
        ReferenciaPricing(
            nombre="plataforma-criptografia-pqc",
            tipo="herramienta-especializada-4-tiers",
            num_clientes=15,
            precio_rango_eur=(199, 1999),
            usuarios_tipicos=5,
            incluye_ia=True,
            notas="4 tiers desde Starter hasta Enterprise; uso intensivo de LLM",
        ),
    ]

    def __init__(self):
        self.client = anthropic.Anthropic()

    def analizar_posicionamiento(
        self,
        tiers_propios: list,
        segmento_objetivo: str,
    ) -> str:
        """
        Uses Claude to analyze pricing positioning
        compared to the market.
        """
        refs_texto = "\n".join([
            f"- {r.nombre}: €{r.precio_rango_eur[0]}-{r.precio_rango_eur[1]}/mes, "
            f"{r.usuarios_tipicos} typical users"
            for r in self.REFERENCIAS
        ])

        tiers_texto = "\n".join([
            f"- {t.nombre}: €{t.precio_mes_eur}/mes, {t.max_usuarios} usuarios, "
            f"margen base {t.margen_base_pct}%"
            for t in tiers_propios
        ])

        prompt = f"""Analyze the pricing positioning of a SaaS platform with AI.

TARGET SEGMENT: {segmento_objetivo}

OUR PRICING STRUCTURE:
{tiers_texto}

MARKET REFERENCES (similar AI platforms):
{refs_texto}

Analyze:
1. Is the pricing competitive for the target segment?
2. Which tier has the most risk of negative margin with heavy users?
3. What price or fair use adjustment would you recommend?
4. Is there a tier the market would demand that we don't offer?

Respond in Spanish, oriented to business decisions.
Maximum 300 words."""

        message = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}]
        )

        return message.content[0].text
