# Extraído de: LibroDevSecOps/cap-17-aiact-pipeline.md
import anthropic
from datetime import datetime

def generate_technical_documentation(
    manifest: dict,
    classification: dict,
    pipeline_artifacts: dict,
    compliance_checks: list[dict]
) -> str:
    """Genera documentación técnica según Anexo IV del AI Act."""
    client = anthropic.Anthropic()

    # Construir contexto con todos los artefactos disponibles
    context = f"""
SISTEMA: {manifest['system']['name']} v{manifest['system']['version']}
CLASIFICACIÓN: {classification['risk_level']} (confianza: {classification['confidence']})
FECHA: {datetime.now().isoformat()}

COMPONENTES IA:
{yaml.dump(manifest.get('ai_components', {}), default_flow_style=False)}

ARTEFACTOS DE SEGURIDAD DISPONIBLES:
- SBOM: {'sí' if pipeline_artifacts.get('sbom') else 'no'}
- SAST results: {pipeline_artifacts.get('sast_summary', 'no disponible')}
- SCA results: {pipeline_artifacts.get('sca_summary', 'no disponible')}
- Prompt injection tests: {pipeline_artifacts.get('prompt_injection_summary', 'no disponible')}
- Logs de uso LLM: {'configurados' if pipeline_artifacts.get('llm_usage_logs') else 'no configurados'}

COMPLIANCE CHECKS:
{_format_checks(compliance_checks)}
"""

    prompt = f"""Genera la documentación técnica para el siguiente sistema de IA
según el Anexo IV del Reglamento (UE) 2024/1689 (AI Act).

{context}

La documentación DEBE contener estas secciones (Anexo IV):
1. Descripción general del sistema de IA
2. Descripción detallada de los elementos y del proceso de desarrollo
3. Información sobre la monitorización, funcionamiento y control
4. Descripción del sistema de gestión de riesgos (Art. 9)
5. Descripción de los cambios realizados durante el ciclo de vida
6. Lista de normas armonizadas aplicadas
7. Copia de la declaración UE de conformidad (si disponible)
8. Descripción del sistema de evaluación del rendimiento post-comercialización

Para cada sección:
- Si hay datos disponibles en los artefactos, úsalos con referencias concretas
- Si faltan datos, marca la sección como "[PENDIENTE - requiere input manual]"
- No inventes datos ni métricas que no estén en el contexto proporcionado

Formato: Markdown con secciones numeradas."""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )

    return response.content[0].text
