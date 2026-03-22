# Extraído de: LibroDevSecOps/cap-15-seguridad-agentes.md
# Definición de herramientas para el agente de triaje
read_findings = SecureTool(
    name="read_scan_results",
    func=fetch_scan_results,       # Lee resultados de Semgrep/Trivy/Grype
    risk_level=RiskLevel.READ,
    description="Lee resultados de escaneos de seguridad del pipeline.",
    max_calls_per_run=10,
)

read_sbom = SecureTool(
    name="read_sbom",
    func=fetch_sbom,               # Lee el SBOM del proyecto
    risk_level=RiskLevel.READ,
    description="Lee el SBOM (CycloneDX) del proyecto.",
    max_calls_per_run=5,
)

analyze_context = SecureTool(
    name="analyze_business_context",
    func=get_service_context,      # Consulta inventario de servicios
    risk_level=RiskLevel.ANALYZE,
    description="Consulta contexto de negocio del servicio afectado.",
    max_calls_per_run=20,
)

classify_finding = SecureTool(
    name="classify_finding",
    func=invoke_claude_classification,  # Llama a Claude para clasificar
    risk_level=RiskLevel.ANALYZE,
    description="Clasifica un hallazgo por severidad real usando Claude.",
    max_calls_per_run=100,
)

# Herramienta que NO debe tener: crear PR (nivel MODIFY)
create_pr = SecureTool(
    name="create_pull_request",
    func=create_github_pr,
    risk_level=RiskLevel.MODIFY,
    description="Crea una pull request en GitHub.",
    max_calls_per_run=5,
)

# Ejecución del agente securizado
runner = SecureAgentRunner(
    permissions=TRIAGE_AGENT_PERMS,  # Solo READ + ANALYZE
    tools=[
        read_findings, read_sbom, analyze_context,
        classify_finding, create_pr,  # create_pr será filtrada
    ],
    system_prompt=(
        "Eres un agente de triaje de seguridad. Tu objetivo es "
        "clasificar los hallazgos de seguridad por prioridad real, "
        "considerando contexto de negocio y explotabilidad. "
        "NO ejecutes acciones de remediación. Solo clasifica e informa."
    ),
)

result = runner.run(
    "Clasifica los 47 hallazgos del último escaneo por prioridad "
    "real. Cruza con el SBOM y el contexto de negocio de cada servicio."
)
