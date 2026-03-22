# Extraído de: LibroTecnico/cap-19-testing-ia.md
        # Verificar regresión en groundedness (bajada = peor)
        if baseline[1] and current[1]:
            change = (float(baseline[1]) - float(current[1])) / max(float(baseline[1]), 0.001)
            if change > regression_threshold:
                regressions.append({
                    "metric": "groundedness_score",
                    "baseline": round(float(baseline[1]), 3),
                    "current": round(float(current[1]), 3),
                    "change_pct": round(change * 100, 1),
                    "direction": "decrease",
                    "severity": "high" if change > 0.30 else "medium",
                })

        return {
            "service": service_type,
            "regressions_detected": len(regressions) > 0,
            "regressions": regressions,
            "recommendation": (
                "Revisar cambios recientes de modelo o prompt" if regressions
                else "Sin anomalías detectadas"
            ),
        }

