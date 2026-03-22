# Extraído de: LibroPQC/cap-26-criptografo-futuro.md
import anthropic
from datetime import datetime, timedelta
from typing import Optional

# Agente de monitorización criptográfica continua
# Vigila cambios en repos, certificados y cloud, y dispara análisis selectivos

client = anthropic.Anthropic()

TOOLS = [
    {
        "name": "check_repo_changes",
        "description": "Detecta commits recientes que modifican ficheros con patrones criptográficos",
        "input_schema": {
            "type": "object",
            "properties": {
                "repo_id": {"type": "integer"},
                "since": {"type": "string", "description": "ISO datetime"}
            },
            "required": ["repo_id", "since"]
        }
    },
    {
        "name": "check_certificate_renewals",
        "description": "Detecta certificados renovados o próximos a expirar",
        "input_schema": {
            "type": "object",
            "properties": {
                "organization_id": {"type": "integer"}
            },
            "required": ["organization_id"]
        }
    },
    {
        "name": "check_cloud_config_drift",
        "description": "Detecta cambios en configuración criptográfica de servicios cloud",
        "input_schema": {
            "type": "object",
            "properties": {
                "cloud_account_id": {"type": "integer"}
            },
            "required": ["cloud_account_id"]
        }
    },
    {
        "name": "analyze_file",
        "description": "Analiza un fichero específico en busca de patrones criptográficos",
        "input_schema": {
            "type": "object",
            "properties": {
                "repo_id": {"type": "integer"},
                "file_path": {"type": "string"}
            },
            "required": ["repo_id", "file_path"]
        }
    },
    {
        "name": "update_crypto_inventory",
        "description": "Actualiza el inventario criptográfico con nuevos hallazgos",
        "input_schema": {
            "type": "object",
            "properties": {
                "finding": {"type": "object"},
                "action": {"type": "string", "enum": ["create", "update", "resolve"]}
            },
            "required": ["finding", "action"]
        }
    }
]

SYSTEM_PROMPT = """Eres un agente de monitorización criptográfica continua.
Tu objetivo es detectar cambios en activos criptográficos de la organización
y actualizar el inventario de preparación post-cuántica.

Prioridades de actuación:
1. CRÍTICO: Nuevos usos de algoritmos quantum-vulnerables en producción
2. ALTO: Certificados renovados con algoritmos no PQC-compliant
3. MEDIO: Cambios en configuración cloud que afecten cifrado
4. BAJO: Actualizaciones de dependencias con implicaciones criptográficas

Cuando detectes un cambio, analiza el impacto, clasifica la severidad
y actualiza el inventario. No generes alertas para cambios irrelevantes.
Sé preciso: un falso positivo erosiona la confianza del equipo."""


def run_monitoring_cycle(
    organization_id: int,
    repos: list[int],
    cloud_accounts: list[int],
    last_check: Optional[str] = None
) -> dict:
    """Ejecuta un ciclo completo de monitorización."""

    since = last_check or (
        datetime.utcnow() - timedelta(hours=24)
    ).isoformat()

    # Prompt inicial: el agente decide qué comprobar primero
    initial_prompt = f"""
    Ejecuta un ciclo de monitorización para la organización {organization_id}.
    Última comprobación: {since}
    Repositorios a vigilar: {repos}
    Cuentas cloud a vigilar: {cloud_accounts}

    Comprueba cambios en repos, certificados y cloud.
    Analiza solo los cambios relevantes para preparación PQC.
    Actualiza el inventario con cada hallazgo nuevo o modificado.
    """

    messages = [{"role": "user", "content": initial_prompt}]
    findings = []
    max_iterations = 15  # Límite de seguridad

    for iteration in range(max_iterations):
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages
        )

        # Procesar tool calls del agente
        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": str(result)
                    })
                    if block.name == "update_crypto_inventory":
                        findings.append(result)

            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})
        else:
            # El agente ha terminado su ciclo
            break

    return {
        "organization_id": organization_id,
        "cycle_completed": datetime.utcnow().isoformat(),
        "iterations": iteration + 1,
        "findings_updated": len(findings),
        "summary": extract_summary(response)
    }
