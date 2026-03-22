# Extraído de: LibroBugBounty/cap-28-economics-bounty.md
# Simulacion con datos de la investigacion (semana de marzo 2026)
roi = MonthlyROI(
    tool_cost_monthly=74.0,
    tax_jurisdiction="spain_autonomo"
)

# 8 Critical (3 posibles duplicados)
for i in range(5):
    roi.add_report(BountyReport(
        f"CRIT-{i+1}", "critical", "direct", 3.0, "accepted"))
for i in range(3):
    roi.add_report(BountyReport(
        f"CRIT-DUP-{i+1}", "critical", "hackerone", 3.0, "duplicate"))

# 14 High (2 rechazados)
for i in range(12):
    roi.add_report(BountyReport(
        f"HIGH-{i+1}", "high", "hackerone", 1.5, "accepted"))
for i in range(2):
    roi.add_report(BountyReport(
        f"HIGH-REJ-{i+1}", "high", "direct", 1.5, "rejected"))

# 10 Medium, 4 Low (todos aceptados)
for i in range(10):
    roi.add_report(BountyReport(
        f"MED-{i+1}", "medium", "bugcrowd", 0.8, "accepted"))
for i in range(4):
    roi.add_report(BountyReport(
        f"LOW-{i+1}", "low", "hackerone", 0.5, "accepted"))

print(json.dumps(roi.summary(), indent=2))
