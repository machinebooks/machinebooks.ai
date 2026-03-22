# Extraído de: LibroDevSecOps/cap-09-agente-triaje.md
from itertools import groupby
from operator import itemgetter

def batch_findings(findings: list[dict]) -> list[list[dict]]:
    """Agrupa hallazgos por servicio y fuente para triaje
    en lotes. Reduce llamadas al agente un 60-70%."""
    # Ordenar por servicio y fuente
    sorted_findings = sorted(
        findings,
        key=lambda f: (f.get("service_name", ""), f["source"])
    )

    batches = []
    for key, group in groupby(
        sorted_findings,
        key=lambda f: (f.get("service_name", ""), f["source"])
    ):
        batch = list(group)
        # Lotes de máximo 15 hallazgos para mantener calidad
        while batch:
            batches.append(batch[:15])
            batch = batch[15:]

    return batches
