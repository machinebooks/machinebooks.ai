# Extraído de: LibroDevSecOps/cap-25-madurez-devsecops.md
# progress_tracker.py — Seguimiento de madurez DevSecOps
from dataclasses import dataclass, field
from datetime import date
import json
from pathlib import Path

@dataclass
class AssessmentSnapshot:
    date: date
    levels: dict[str, int]       # dominio -> nivel alcanzado
    global_score: float
    criteria_detail: dict[str, dict[str, bool]]  # dominio -> {criterio: cumplido}
    assessor: str                # Quién ejecutó el assessment
    notes: str = ""

@dataclass
class MaturityTracker:
    organization: str
    profile: str                 # "startup", "enterprise_ai", "public_regulated"
    snapshots: list[AssessmentSnapshot] = field(default_factory=list)

    def add_snapshot(self, snapshot: AssessmentSnapshot) -> None:
        self.snapshots.append(snapshot)
        self.snapshots.sort(key=lambda s: s.date)

    def get_trend(self, domain: str) -> list[tuple[date, int]]:
        """Devuelve la serie temporal de nivel para un dominio."""
        return [(s.date, s.levels.get(domain, 0)) for s in self.snapshots]

    def get_improvement_rate(self, domain: str) -> float:
        """Calcula la tasa de mejora (niveles/mes) para un dominio."""
        trend = self.get_trend(domain)
        if len(trend) < 2:
            return 0.0
        first_date, first_level = trend[0]
        last_date, last_level = trend[-1]
        months = max((last_date - first_date).days / 30.0, 1.0)
        return round((last_level - first_level) / months, 3)

    def domains_below_target(
        self, targets: dict[str, int]
    ) -> list[tuple[str, int, int]]:
        """Identifica dominios por debajo del objetivo."""
        if not self.snapshots:
            return [(d, 0, t) for d, t in targets.items()]
        current = self.snapshots[-1].levels
        return [
            (domain, current.get(domain, 0), target)
            for domain, target in targets.items()
            if current.get(domain, 0) < target
        ]

    def save(self, path: Path) -> None:
        """Persiste el histórico de assessments."""
        data = {
            "organization": self.organization,
            "profile": self.profile,
            "snapshots": [
                {
                    "date": s.date.isoformat(),
                    "levels": s.levels,
                    "global_score": s.global_score,
                    "assessor": s.assessor,
                    "notes": s.notes,
                }
                for s in self.snapshots
            ]
        }
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
