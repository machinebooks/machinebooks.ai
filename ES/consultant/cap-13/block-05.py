# Extraído de: LibroConsultor/cap-13-gap-analysis.md
from datetime import date, timedelta


@dataclass
class RemediationAction:
    """Una acción concreta en el roadmap."""
    gap: GapFinding
    phase: str              # "quick_win", "consolidacion", "maduracion"
    start_date: date
    end_date: date
    effort_days: float
    dependencies: list[str] = field(default_factory=list)
    responsible_role: str = ""


class RoadmapGenerator:
    """Genera roadmap de remediación a partir de gaps."""

    PHASE_RULES = {
        "quick_win": {
            "max_effort": 5,
            "priority": ["critica", "alta"],
            "duration_months": 3,
        },
        "consolidacion": {
            "max_effort": 20,
            "priority": ["critica", "alta", "media"],
            "duration_months": 9,
        },
        "maduracion": {
            "max_effort": float("inf"),
            "priority": ["critica", "alta", "media", "baja"],
            "duration_months": 12,
        },
    }

    def generate(
        self,
        gaps: list[GapFinding],
        start: date,
        available_capacity_days_month: float = 20,
    ) -> list[RemediationAction]:
        """Genera roadmap con tres fases de remediación."""
        actions: list[RemediationAction] = []
        current_date = start

        for phase_name, rules in self.PHASE_RULES.items():
            phase_gaps = [
                g for g in gaps
                if g.effort_days <= rules["max_effort"]
                and g.priority in rules["priority"]
                and g not in [a.gap for a in actions]
            ]
            # Ordenar por prioridad y luego por esfuerzo
            phase_gaps.sort(
                key=lambda g: (
                    ["critica", "alta", "media", "baja"]
                    .index(g.priority),
                    g.effort_days,
                )
            )

            phase_end = current_date + timedelta(
                days=rules["duration_months"] * 30
            )
            accumulated_days = 0

            for gap in phase_gaps:
                if accumulated_days + gap.effort_days > (
                    available_capacity_days_month
                    * rules["duration_months"]
                ):
                    break  # Excede capacidad de la fase

                action = RemediationAction(
                    gap=gap,
                    phase=phase_name,
                    start_date=current_date + timedelta(
                        days=int(accumulated_days * 1.5)
                    ),
                    end_date=current_date + timedelta(
                        days=int(
                            (accumulated_days + gap.effort_days)
                            * 1.5
                        )
                    ),
                    effort_days=gap.effort_days,
                    responsible_role=self._assign_role(gap),
                )
                actions.append(action)
                accumulated_days += gap.effort_days

            current_date = phase_end

        return actions

    def _assign_role(self, gap: GapFinding) -> str:
        """Asigna rol responsable según categoría del gap."""
        role_map = {
            "Organizativas": "CISO / Responsable de Seguridad",
            "Personas": "RRHH + Seguridad",
            "Tecnológicas": "Equipo de Sistemas / DevSecOps",
            "Físicas": "Facility Management + Seguridad",
        }
        return role_map.get(
            gap.control.category,
            "Equipo de Seguridad",
        )
