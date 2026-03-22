# Source: The FinOps Engineer and the Machine -- Chapter 27
# Pattern: SaaS pricing calculator with cost model

# services/pricing_calculator.py
# Calculator that determines public pricing from real costs.
# Considers user mix, fair use and target margins.

from dataclasses import dataclass, field
from typing import Optional
import anthropic


@dataclass
class PerfilUsoEstimado:
    """Estimated distribution of user types for a customer."""
    pct_heavy: float    # % of heavy users (high usage)
    pct_average: float  # % of average users
    pct_light: float    # % of light users

    # Monthly cost per profile (EUR) — based on real system data
    COSTE_HEAVY = 8.50   # EUR 8.50/month (proportional token + cloud mix)
    COSTE_AVERAGE = 3.60 # EUR 3.60/month
    COSTE_LIGHT = 0.06   # EUR 0.06/month

    def coste_promedio_usuario(self) -> float:
        return (
            self.pct_heavy * self.COSTE_HEAVY +
            self.pct_average * self.COSTE_AVERAGE +
            self.pct_light * self.COSTE_LIGHT
        )


@dataclass
class TierPricing:
    """A pricing level in the pricing structure."""
    nombre: str
    max_usuarios: int
    precio_mes_eur: float
    precio_usuario_mes: float  # precio_mes / max_usuarios
    margen_base_pct: float     # margin with average user mix

    # Fair use limits
    operaciones_analisis_mes: int   # max analysis operations per user
    documentos_procesados_mes: int  # max documents processed per user

    # Margin sensitivity analysis
    margen_con_heavy_users_pct: float   # margin if 60% heavy users
    margen_con_light_users_pct: float   # margin if 80% light users


class PricingCalculator:
    """
    Calculates the optimal pricing structure for a SaaS with integrated AI.

    The inputs are:
    - Variable costs per user profile
    - Monthly fixed costs of the platform
    - Target margin (minimum and target)
    - Historical data on usage profile distribution

    The output is a tier structure with margin analysis.
    """

    def __init__(
        self,
        coste_fijo_mensual_eur: float,  # Base hosting, licenses, support
        margen_minimo_pct: float = 0.45,
        margen_objetivo_pct: float = 0.65,
    ):
        self.coste_fijo = coste_fijo_mensual_eur
        self.margen_minimo = margen_minimo_pct
        self.margen_objetivo = margen_objetivo_pct

        # Historical distribution of usage profiles (from LLMUsageLog)
        self.distribucion_real = PerfilUsoEstimado(
            pct_heavy=0.08,
            pct_average=0.67,
            pct_light=0.25,
        )

        # Worst case distribution (for sensitivity analysis)
        self.distribucion_heavy = PerfilUsoEstimado(
            pct_heavy=0.60,
            pct_average=0.30,
            pct_light=0.10,
        )

    def calcular_precio_minimo_tier(self, num_usuarios: int) -> float:
        """
        Calculates the minimum price for a tier of N users.
        Guarantees minimum margin even in the worst case user distribution.
        """
        # Variable cost with heavy distribution (worst case)
        coste_variable_worst = (
            self.distribucion_heavy.coste_promedio_usuario() * num_usuarios
        )

        # Total cost including proportional fixed overhead
        coste_fijo_proporcional = self.coste_fijo / 100 * num_usuarios  # EUR/user from fixed costs
        coste_total = coste_variable_worst + coste_fijo_proporcional

        # Minimum price to cover minimum margin in worst case
        precio_minimo = coste_total / (1 - self.margen_minimo)

        return precio_minimo

    def calcular_tier(self, nombre: str, max_usuarios: int) -> TierPricing:
"""Calculates a complete tier with all margin analyses."""
        precio_minimo = self.calcular_precio_minimo_tier(max_usuarios)

        # Add margin to reach target with real distribution
        coste_variable_real = (
            self.distribucion_real.coste_promedio_usuario() * max_usuarios
        )
        precio_objetivo = coste_variable_real / (1 - self.margen_objetivo)

        # Final price is the maximum between minimum and target
        precio_final = max(precio_minimo, precio_objetivo)

        # Round to an attractive marketing number
        precio_final = self._redondear_precio_marketing(precio_final)

        # Calculate margins for analysis
        def calcular_margen(precio, distribucion, n_usuarios):
            coste = distribucion.coste_promedio_usuario() * n_usuarios
            return (precio - coste) / precio

        margen_base = calcular_margen(precio_final, self.distribucion_real, max_usuarios)
        margen_heavy = calcular_margen(precio_final, self.distribucion_heavy, max_usuarios)
        distribucion_light = PerfilUsoEstimado(0.02, 0.18, 0.80)
        margen_light = calcular_margen(precio_final, distribucion_light, max_usuarios)

        return TierPricing(
            nombre=nombre,
            max_usuarios=max_usuarios,
            precio_mes_eur=precio_final,
            precio_usuario_mes=round(precio_final / max_usuarios, 2),
            margen_base_pct=round(margen_base * 100, 1),
            operaciones_analisis_mes=max_usuarios * 300,
            documentos_procesados_mes=max_usuarios * 50,
            margen_con_heavy_users_pct=round(margen_heavy * 100, 1),
            margen_con_light_users_pct=round(margen_light * 100, 1),
        )

    def _redondear_precio_marketing(self, precio: float) -> float:
        """Rounds to the nearest attractive marketing number."""
        # Standard ranges and rounding in European B2B SaaS
        if precio < 100:
            return round(precio / 9) * 9 + (49 if precio < 50 else 99)
        elif precio < 300:
            return round(precio / 25) * 25
        elif precio < 1000:
            return round(precio / 50) * 50
        else:
            return round(precio / 100) * 100

    def generar_estructura_completa(self) -> list[TierPricing]:
        """Generates the complete pricing structure."""
        return [
            self.calcular_tier("Starter", 10),
            self.calcular_tier("Professional", 25),
            self.calcular_tier("Business", 50),
            self.calcular_tier("Enterprise", 100),
        ]
