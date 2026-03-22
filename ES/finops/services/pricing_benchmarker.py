# Extraído de: LibroFinOps/cap-27-caso-pricing-saas.md
# services/pricing_benchmarker.py
# Benchmarking de pricing contra referencias del mercado conocidas.
# Usa Claude para análisis cualitativo de posicionamiento.

import anthropic
from dataclasses import dataclass


@dataclass
class ReferenciaPricing:
    """Dato de referencia de pricing de una plataforma similar."""
    nombre: str          # Nombre genérico (no identificador real)
    tipo: str            # "plataforma-seguridad", "plataforma-pqc", etc.
    num_clientes: int
    precio_rango_eur: tuple[float, float]  # (min, max) por mes
    usuarios_tipicos: int
    incluye_ia: bool
    notas: str


class PricingBenchmarker:
    """
    Compara la estructura de pricing propia con referencias del mercado.
    """

    # Referencias del mercado (datos de las otras plataformas de la serie)
    # Los datos son aproximados y anonimizados
    REFERENCIAS = [
        ReferenciaPricing(
            nombre="plataforma-seguridad-ofensiva",
            tipo="herramienta-especializada",
            num_clientes=20,
            precio_rango_eur=(580, 675),
            usuarios_tipicos=3,
            incluye_ia=True,
            notas="Plataforma de auditoría con IA para análisis de vulnerabilidades",
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
        Usa Claude para analizar el posicionamiento de pricing
        respecto al mercado.
        """
        refs_texto = "\n".join([
            f"- {r.nombre}: €{r.precio_rango_eur[0]}-{r.precio_rango_eur[1]}/mes, "
            f"{r.usuarios_tipicos} usuarios típicos"
            for r in self.REFERENCIAS
        ])

        tiers_texto = "\n".join([
            f"- {t.nombre}: €{t.precio_mes_eur}/mes, {t.max_usuarios} usuarios, "
            f"margen base {t.margen_base_pct}%"
            for t in tiers_propios
        ])

        prompt = f"""Analiza el posicionamiento de pricing de una plataforma SaaS con IA.

SEGMENTO OBJETIVO: {segmento_objetivo}

NUESTRA ESTRUCTURA DE PRICING:
{tiers_texto}

REFERENCIAS DEL MERCADO (plataformas con IA similares):
{refs_texto}

Analiza:
1. ¿El pricing es competitivo para el segmento objetivo?
2. ¿Qué tier tiene más riesgo de margen negativo con heavy users?
3. ¿Qué ajuste de precio o fair use recomendarías?
4. ¿Hay un tier que el mercado demandaría y no ofrecemos?

Responde en español, orientado a decisiones de negocio.
Máximo 300 palabras."""

        message = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}]
        )

        return message.content[0].text
