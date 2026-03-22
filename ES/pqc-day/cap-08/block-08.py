# Extraído de: LibroPQC/cap-08-certificados.md
valid_results = [r for r in self.results if r.is_valid]
avg_pqc_score = (
    sum(r.pqc_readiness_score for r in valid_results)
    / len(valid_results)
) if valid_results else 0
