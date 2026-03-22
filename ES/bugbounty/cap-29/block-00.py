# Extraído de: LibroBugBounty/cap-29-futuro-hunter.md
"""
attack_surface_monitor.py -- Monitor de superficies de ataque emergentes
Rastrea nuevos programas de bounty, CVEs en categorias de interes,
y tendencias en repositorios de seguridad para guiar la investigacion.
"""
import anthropic
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional

@dataclass
class AttackSurface:
    """Superficie de ataque monitorizada."""
    name: str
    category: str          # ai_assistant, electron, driver, iot, automotive
    maturity: str          # emerging, growing, mature, declining
    competition: str       # low, medium, high
    avg_bounty_critical: float
    avg_bounty_high: float
    hunter_skill_match: float  # 0.0-1.0 match con nuestras habilidades
    notes: str = ""
    
    @property
    def opportunity_score(self) -> float:
        """Score de oportunidad: bounty * match / competencia."""
        comp_factor = {"low": 3.0, "medium": 1.5, "high": 0.5}
        mat_factor = {"emerging": 2.0, "growing": 1.5, "mature": 0.8, "declining": 0.3}
        return (
            (self.avg_bounty_critical / 1000) *
            self.hunter_skill_match *
            comp_factor.get(self.competition, 1.0) *
            mat_factor.get(self.maturity, 1.0)
        )

# Superficies de ataque conocidas (marzo 2026)
SURFACES = [
    AttackSurface(
        "AI Coding Assistants", "ai_assistant", "emerging", "low",
        avg_bounty_critical=15000, avg_bounty_high=5000,
        hunter_skill_match=0.9,
        notes="Copilot, Claude Desktop, Wand, Cursor, Windsurf"
    ),
    AttackSurface(
        "AI Desktop Apps (non-IDE)", "ai_assistant", "emerging", "low",
        avg_bounty_critical=10000, avg_bounty_high=3000,
        hunter_skill_match=0.85,
        notes="ChatGPT Desktop, Gemini, Perplexity, Notion AI"
    ),
    AttackSurface(
        "Electron Apps (gaming/comms)", "electron", "growing", "medium",
        avg_bounty_critical=5000, avg_bounty_high=2000,
        hunter_skill_match=0.95,
        notes="Discord, Slack, Teams, Spotify"
    ),
    AttackSurface(
        "Windows Kernel Drivers", "driver", "mature", "low",
        avg_bounty_critical=8000, avg_bounty_high=3000,
        hunter_skill_match=0.8,
        notes="ASUS, MSI, Razer, Corsair (hardware vendors)"
    ),
    AttackSurface(
        "IoT Consumer Devices", "iot", "growing", "medium",
        avg_bounty_critical=3000, avg_bounty_high=1000,
        hunter_skill_match=0.4,
        notes="Requiere hardware fisico; menor match de skills"
    ),
    AttackSurface(
        "Web Applications (classic)", "web", "mature", "high",
        avg_bounty_critical=3000, avg_bounty_high=1000,
        hunter_skill_match=0.6,
        notes="Alta competencia, bugs faciles ya encontrados"
    ),
    AttackSurface(
        "LLM Provider APIs", "ai_assistant", "emerging", "low",
        avg_bounty_critical=50000, avg_bounty_high=15000,
        hunter_skill_match=0.7,
        notes="Anthropic, OpenAI, Google AI — pagos altos"
    ),
]

def rank_opportunities(surfaces: list[AttackSurface]) -> list[dict]:
    """Rankea superficies de ataque por oportunidad."""
    ranked = sorted(surfaces, key=lambda s: s.opportunity_score, reverse=True)
    return [
        {
            "rank": i + 1,
            "surface": s.name,
            "category": s.category,
            "maturity": s.maturity,
            "competition": s.competition,
            "score": round(s.opportunity_score, 1),
            "avg_critical_bounty": f"${s.avg_bounty_critical:,.0f}",
            "notes": s.notes,
        }
        for i, s in enumerate(ranked)
    ]

# Ranking de oportunidades
for opp in rank_opportunities(SURFACES):
    print(f"#{opp['rank']} {opp['surface']} "
          f"(score: {opp['score']}, {opp['competition']} competition, "
          f"critical: {opp['avg_critical_bounty']})")
