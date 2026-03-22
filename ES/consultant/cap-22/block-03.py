# Extraído de: LibroConsultor/cap-22-unit-economics.md
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class ProjectRecord:
    """Registro de un proyecto completado."""
    project_id: str
    consultant: str
    project_type: str               # "audit", "assessment", "proposal", "advisory"
    client_sector: str
    # Línea base (sin IA)
    baseline_hours: float            # Estimación de horas sin IA
    baseline_price: float            # Precio que se habría cobrado sin IA
    # Real (con IA)
    actual_hours: float              # Horas reales invertidas
    actual_price: float              # Precio cobrado
    ai_cost: float                   # Coste de tokens + infra para este proyecto
    # Metadatos
    start_date: datetime = field(default_factory=datetime.now)
    end_date: Optional[datetime] = None
    satisfaction_score: Optional[int] = None  # 1-10 del cliente

    @property
    def hours_saved(self) -> float:
        return max(0, self.baseline_hours - self.actual_hours)

    @property
    def compression_actual(self) -> float:
        if self.baseline_hours == 0:
            return 0
        return self.hours_saved / self.baseline_hours

    @property
    def price_retention_actual(self) -> float:
        if self.baseline_price == 0:
            return 0
        return self.actual_price / self.baseline_price

    @property
    def incremental_margin(self) -> float:
        """Margen incremental atribuible a la IA."""
        cost_rate = 58  # Coste/hora del consultor
        baseline_margin = self.baseline_price - (self.baseline_hours * cost_rate)
        actual_margin = (self.actual_price
                         - (self.actual_hours * cost_rate)
                         - self.ai_cost)
        return actual_margin - baseline_margin


@dataclass
class ROITracker:
    """Acumula y analiza el ROI de IA en la práctica."""
    records: List[ProjectRecord] = field(default_factory=list)

    def add_project(self, record: ProjectRecord) -> None:
        self.records.append(record)

    @property
    def total_hours_saved(self) -> float:
        return sum(r.hours_saved for r in self.records)

    @property
    def total_incremental_margin(self) -> float:
        return sum(r.incremental_margin for r in self.records)

    @property
    def total_ai_cost(self) -> float:
        return sum(r.ai_cost for r in self.records)

    @property
    def aggregate_roi(self) -> float:
        if self.total_ai_cost == 0:
            return 0
        return self.total_incremental_margin / self.total_ai_cost

    @property
    def avg_compression(self) -> float:
        if not self.records:
            return 0
        return sum(r.compression_actual for r in self.records) / len(self.records)

    def by_project_type(self) -> dict:
        """ROI desglosado por tipo de proyecto."""
        types: dict = {}
        for r in self.records:
            if r.project_type not in types:
                types[r.project_type] = []
            types[r.project_type].append(r)

        summary = {}
        for ptype, projects in types.items():
            total_ai = sum(p.ai_cost for p in projects)
            total_inc = sum(p.incremental_margin for p in projects)
            avg_comp = sum(p.compression_actual for p in projects) / len(projects)
            summary[ptype] = {
                "projects": len(projects),
                "avg_compression": f"{avg_comp:.0%}",
                "total_ai_cost": round(total_ai, 2),
                "total_incremental_margin": round(total_inc, 2),
                "roi": f"{total_inc / total_ai:.1f}x" if total_ai > 0 else "N/A",
            }
        return summary
