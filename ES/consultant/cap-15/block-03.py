# Extraído de: LibroConsultor/cap-15-madurez-ia.md
@dataclass
class BenchmarkComparison:
    dimension: Dimension
    client_score: float
    sector_median: float
    sector_p25: float      # Percentil 25
    sector_p75: float      # Percentil 75
    size_band_median: float
    position: str          # "por debajo", "en la media", "por encima"
    gap_to_median: float

def benchmark_against_sector(
    assessment: MaturityAssessment,
    benchmark_db: list[dict]
) -> list[BenchmarkComparison]:
    """Compara el assessment contra benchmarks sectoriales."""

    # Filtrar benchmarks relevantes
    sector_benchmarks = [
        b for b in benchmark_db
        if b["sector"] == assessment.sector
    ]
    size_benchmarks = [
        b for b in sector_benchmarks
        if b["size_band"] == assessment.size_band
    ]

    comparisons = []
    for dim_score in assessment.dimensions:
        dim_key = dim_score.dimension.value

        # Calcular estadísticos del sector
        sector_scores = [b["scores"][dim_key] for b in sector_benchmarks]
        size_scores = [b["scores"][dim_key] for b in size_benchmarks]

        sector_med = _median(sector_scores)
        client_gap = round(dim_score.level - sector_med, 1)

        comparisons.append(BenchmarkComparison(
            dimension=dim_score.dimension,
            client_score=dim_score.level,
            sector_median=sector_med,
            sector_p25=_percentile(sector_scores, 25),
            sector_p75=_percentile(sector_scores, 75),
            size_band_median=_median(size_scores) if size_scores else sector_med,
            position=_classify_position(dim_score.level, sector_med),
            gap_to_median=client_gap,
        ))

    return comparisons
