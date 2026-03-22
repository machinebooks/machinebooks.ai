# Extraído de: LibroPQC/cap-09-auditoria-cloud.md
# Ejemplo didáctico: analyzers/cloud_security_analyzer.py

def _calculate_pqc_readiness_score(self) -> float:
    """Calcula puntuación de preparación PQC (0-100)"""
    if not self.findings:
        return 100.0

    # Penalización por severidad
    weights = {
        'critical': 25,   # Cada hallazgo crítico resta 25 puntos
        'high': 15,        # Cada hallazgo alto resta 15 puntos
        'medium': 8,       # Cada hallazgo medio resta 8 puntos
        'low': 3,          # Cada hallazgo bajo resta 3 puntos
        'info': 1           # Cada hallazgo informativo resta 1 punto
    }
    total_penalty = sum(weights.get(f.severity, 0) for f in self.findings)

    # Tope máximo de 100 puntos de penalización
    total_penalty = min(total_penalty, 100)

    return max(0, 100 - total_penalty)
