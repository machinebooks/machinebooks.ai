# Extraído de: LibroConsultor/cap-05-agentes-analisis.md
import asyncio

async def run_compliance_analysis(
    client_id: str,
    project_id: str,
    framework: str,
    sections: list[str]
) -> list[dict]:
    """Ejecuta un análisis de cumplimiento completo contra
    las secciones especificadas de un framework."""

    agent = create_compliance_agent(client_id, project_id)
    all_findings = []

    for section in sections:
        # El agente recibe la instrucción y decide qué herramientas usar
        result = await agent.run(
            f"Evalúa el cumplimiento del cliente contra la sección "
            f"'{section}' del framework '{framework}'. "
            f"Consulta el framework, busca evidencias, revisa hallazgos "
            f"previos si existen y produce un hallazgo estructurado "
            f"para cada control de la sección."
        )

        # Extrae hallazgos del resultado del agente
        findings = extract_findings(result)
        all_findings.extend(findings)

        # Log de progreso para el consultor
        low_confidence = [f for f in findings if f["confianza"] < 0.5]
        print(
            f"[{section}] {len(findings)} hallazgos | "
            f"{len(low_confidence)} requieren revisión humana"
        )

    return all_findings

# Ejemplo de ejecución
findings = asyncio.run(run_compliance_analysis(
    client_id="CLIENTE_FIN_2026",
    project_id="GAP_ENS_Q1",
    framework="ens",
    sections=["op.pl", "op.acc", "op.exp", "op.ext",
              "mp.if", "mp.per", "mp.eq", "mp.com",
              "mp.si", "mp.sw", "mp.info", "mp.s"]
))
