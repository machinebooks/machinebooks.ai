# Extraído de: LibroPQC/cap-07-analisis-codigo.md
def _calculate_pqc_readiness(self) -> float:
    """Calcula el score de preparación PQC (0-100)"""
    if not self.findings:
        return 100.0  # Sin hallazgos = completamente preparado

    # Pesos por severidad: critical penaliza mucho más que medium
    weights = {'critical': 20, 'high': 12, 'medium': 6, 'low': 2, 'info': 0}
    total_penalty = sum(weights.get(f.severity, 0) for f in self.findings)

    # Normalizar por ficheros escaneados para comparar
    # repositorios de tamaños diferentes
    if self.files_scanned > 0:
        normalized_penalty = (total_penalty / self.files_scanned) * 10
    else:
        normalized_penalty = total_penalty

    return max(0, 100 - min(normalized_penalty, 100))
