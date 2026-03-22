# Extraído de: LibroBugBounty/cap-08-analisis-drivers.md
def main():
    drivers = sorted(Path("/lab/drivers").glob("*.sys"))
    all_reports = []
    for driver in drivers:
        report = analyze_pe(driver)
        all_reports.append(report)
        # Score de riesgo automático: prioriza investigación
        if report["risk_score"] >= 9:
            print(f"[!] {driver.name}: CRITICAL — investigar primero")
        elif report["risk_score"] >= 6:
            print(f"[*] {driver.name}: HIGH — investigar segundo")

    # Guardar informe completo en JSON
    with open("/lab/results/pe_analysis_report.json", "w") as f:
        json.dump(all_reports, f, indent=2, default=str)
