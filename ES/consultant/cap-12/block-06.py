# Extraído de: LibroConsultor/cap-12-auditorias-automatizadas.md
def run_full_audit(
    framework_key: str,
    docs_folder: str,
    config_path: str = "audit_config.yaml"
):
    """Flujo completo de auditoría asistida por agente."""
    import yaml
    from datetime import datetime

    # 1. Cargar configuración
    with open(config_path) as f:
        config = yaml.safe_load(f)
    fw_config = config["frameworks"][framework_key]
    settings = config["audit_settings"]

    # 2. Inicializar agente y recolector
    agent = AuditAgent(
        framework=fw_config["name"],
        model=settings["evaluation_model"]
    )
    agent.load_framework(fw_config["controls_file"])
    collector = EvidenceCollector()

    # 3. Ingesta y triaje
    print(f"Iniciando auditoría {fw_config['name']}")
    print(f"Documentos en: {docs_folder}")
    agent.ingest_documents(docs_folder)

    # 4. Evaluación de controles
    print(f"\nEvaluando {len(agent.controls)} controles...")
    findings = agent.run_audit()

    # 5. Generar entregables
    report = {
        "audit_framework": fw_config["name"],
        "date": datetime.now().isoformat(),
        "status": "BORRADOR — PENDIENTE REVISIÓN HUMANA",
        "statistics": agent._calculate_stats(),
        "findings": [vars(f) for f in findings],
        "evidence_matrix": collector.generate_evidence_matrix(),
    }

    # 6. Guardar borrador
    output_path = f"audit_{framework_key}_{datetime.now():%Y%m%d}.json"
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\nBorrador generado: {output_path}")
    print("⚠ REQUIERE REVISIÓN HUMANA antes de entregar al cliente")

    return report
