# Extraído de: LibroTecnico/cap-09-servicios-negocio.md
@dataclass
class DocumentRequirement:
    """Requisito extraído de un documento de requisitos."""
    id: str
    name: str
    category: str       # 'tecnico', 'funcional', 'organizativo', 'economico'
    description: str
    source_section: str  # Sección del documento original
    priority: str        # 'obligatorio', 'valorable', 'opcional'
    coverage_status: str # 'pending', 'covered', 'partial', 'gap'

@dataclass
class AnalysisResult:
    """Resultado completo del análisis."""
    status: str          # 'extracting', 'matching', 'analyzing', 'completed'
    progress: int        # 0-100
    total_requirements: int
    covered_count: int
    partial_count: int
    gap_count: int
    coverage_percentage: float
    go_decision: str     # 'GO', 'NO-GO', 'CONDICIONAL'
    risk_level: str      # 'bajo', 'medio', 'alto', 'critico'
