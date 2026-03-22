# Extraído de: LibroBugBounty/cap-28-economics-bounty.md
"""
hunter_service_pricing.py -- Modelo de pricing para
servicios de security research asistido por IA.
Calcula tarifas competitivas basadas en productividad con IA.
"""
@dataclass
class HunterServiceTier:
    """Tier de servicio de security research."""
    name: str
    hours_per_month: int
    targets_included: int
    report_format: str          # basic, detailed, executive
    ai_assisted: bool = True
    
    @property
    def base_rate_hourly(self) -> float:
        """Tarifa base por hora segun tier."""
        rates = {
            "starter": 75,    # reports basicos, apps web
            "professional": 150,  # reports detallados, desktop + web
            "enterprise": 250,    # executive reports, kernel + IA + desktop
        }
        return rates.get(self.name, 100)
    
    @property
    def monthly_price(self) -> float:
        """Precio mensual del servicio."""
        return self.base_rate_hourly * self.hours_per_month
    
    @property
    def effective_hourly_with_ai(self) -> float:
        """Tarifa efectiva considerando multiplicador IA (4-5x)."""
        if self.ai_assisted:
            return self.base_rate_hourly * 4.5  # valor entregado/hora
        return self.base_rate_hourly

# Tiers de servicio
tiers = [
    HunterServiceTier("starter", 20, 3, "basic"),
    HunterServiceTier("professional", 40, 8, "detailed"),
    HunterServiceTier("enterprise", 60, 15, "executive"),
]

for tier in tiers:
    print(f"{tier.name}: ${tier.monthly_price:,.0f}/mes "
          f"({tier.hours_per_month}h, {tier.targets_included} targets)")
    print(f"  Valor IA efectivo: ${tier.effective_hourly_with_ai:.0f}/h")
