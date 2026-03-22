# Extraído de: LibroFinOps/cap-27-caso-pricing-saas.md
# services/pricing_calculator.py
# Calculadora que determina el pricing público desde los costes reales.
# Considera mix de usuarios, fair use y márgenes objetivo.

from dataclasses import dataclass, field
from typing import Optional
import anthropic


@dataclass
class PerfilUsoEstimado:
    """Distribución estimada de tipos de usuario para un cliente."""
    pct_heavy: float    # % de usuarios heavy (high usage)
    pct_average: float  # % de usuarios average
    pct_light: float    # % de usuarios light

    # Coste mensual por perfil (€) — basado en datos reales del sistema
    COSTE_HEAVY = 8.50   # €8.50/mes (mix tokens + cloud proporcionado)
    COSTE_AVERAGE = 3.60 # €3.60/mes
    COSTE_LIGHT = 0.06   # €0.06/mes

    def coste_promedio_usuario(self) -> float:
        return (
            self.pct_heavy * self.COSTE_HEAVY +
            self.pct_average * self.COSTE_AVERAGE +
            self.pct_light * self.COSTE_LIGHT
        )


@dataclass
class TierPricing:
    """Un nivel de pricing en la estructura tarifaria."""
    nombre: str
    max_usuarios: int
    precio_mes_eur: float
    precio_usuario_mes: float  # precio_mes / max_usuarios
    margen_base_pct: float     # margen con mix de usuarios promedio

    # Límites de fair use
    operaciones_analisis_mes: int   # máx operaciones de análisis por usuario
    documentos_procesados_mes: int  # máx documentos procesados por usuario

    # Análisis de sensibilidad de márgenes
    margen_con_heavy_users_pct: float   # margen si 60% heavy users
    margen_con_light_users_pct: float   # margen si 80% light users


class PricingCalculator:
    """
    Calcula la estructura de pricing óptima para un SaaS con IA integrada.

    Los inputs son:
    - Costes variables por perfil de usuario
    - Costes fijos mensuales de la plataforma
    - Margen objetivo (mínimo y objetivo)
    - Datos históricos de distribución de perfiles de uso

    El output es una estructura de tiers con análisis de márgenes.
    """

    def __init__(
        self,
        coste_fijo_mensual_eur: float,  # Hosting base, licencias, soporte
        margen_minimo_pct: float = 0.45,
        margen_objetivo_pct: float = 0.65,
    ):
        self.coste_fijo = coste_fijo_mensual_eur
        self.margen_minimo = margen_minimo_pct
        self.margen_objetivo = margen_objetivo_pct

        # Distribución histórica de perfiles de uso (de LLMUsageLog)
        self.distribucion_real = PerfilUsoEstimado(
            pct_heavy=0.08,
            pct_average=0.67,
            pct_light=0.25,
        )

        # Distribución worst case (para análisis de sensibilidad)
        self.distribucion_heavy = PerfilUsoEstimado(
            pct_heavy=0.60,
            pct_average=0.30,
            pct_light=0.10,
        )

    def calcular_precio_minimo_tier(self, num_usuarios: int) -> float:
        """
        Calcula el precio mínimo para un tier de N usuarios.
        Garantiza el margen mínimo incluso en el peor caso de distribución de usuarios.
        """
        # Coste variable con distribución heavy (worst case)
        coste_variable_worst = (
            self.distribucion_heavy.coste_promedio_usuario() * num_usuarios
        )

        # Coste total incluyendo overhead fijo proporcional
        coste_fijo_proporcional = self.coste_fijo / 100 * num_usuarios  # €/usuario del fijo
        coste_total = coste_variable_worst + coste_fijo_proporcional

        # Precio mínimo para cubrir margen mínimo en worst case
        precio_minimo = coste_total / (1 - self.margen_minimo)

        return precio_minimo

    def calcular_tier(self, nombre: str, max_usuarios: int) -> TierPricing:
        """Calcula un tier completo con todos los análisis de margen."""
        precio_minimo = self.calcular_precio_minimo_tier(max_usuarios)

        # Añadir margen para llegar al objetivo con distribución real
        coste_variable_real = (
            self.distribucion_real.coste_promedio_usuario() * max_usuarios
        )
        precio_objetivo = coste_variable_real / (1 - self.margen_objetivo)

        # El precio final es el máximo entre mínimo y objetivo
        precio_final = max(precio_minimo, precio_objetivo)

        # Redondear a número de marketing atractivo
        precio_final = self._redondear_precio_marketing(precio_final)

        # Calcular márgenes para el análisis
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
        """Redondea al número de marketing más cercano y atractivo."""
        # Rangos y redondeos estándar en SaaS B2B europeo
        if precio < 100:
            return round(precio / 9) * 9 + (49 if precio < 50 else 99)
        elif precio < 300:
            return round(precio / 25) * 25
        elif precio < 1000:
            return round(precio / 50) * 50
        else:
            return round(precio / 100) * 100

    def generar_estructura_completa(self) -> list[TierPricing]:
        """Genera la estructura completa de pricing."""
        return [
            self.calcular_tier("Starter", 10),
            self.calcular_tier("Professional", 25),
            self.calcular_tier("Business", 50),
            self.calcular_tier("Enterprise", 100),
        ]
