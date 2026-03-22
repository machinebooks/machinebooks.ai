# Extraído de: LibroDevSecOps/cap-13-prompt-injection.md
from claude_agent_sdk import Agent, tool

@tool
def scan_document_for_injection(
    document_text: str,
    source: str
) -> dict:
    """Escanea un documento antes de indexarlo en el RAG."""
    # Buscar instrucciones embebidas en el documento
    suspicious_patterns = [
        r"(?i)(ignore|ignora|olvida).{0,30}(instrucciones|instructions|rules)",
        r"(?i)(eres|you are).{0,20}(ahora|now)",
        r"(?i)(system|sistema).{0,10}(prompt|override|anular)",
        r"<!--.*?-->",                    # Comentarios HTML ocultos
        r"\u200b|\u200c|\u200d|\ufeff",   # Caracteres de ancho cero
    ]
    findings = []
    for pattern in suspicious_patterns:
        matches = re.finditer(pattern, document_text)
        for match in matches:
            findings.append({
                "pattern": pattern,
                "match": match.group()[:100],
                "position": match.start(),
                "source": source
            })
    return {
        "is_safe": len(findings) == 0,
        "findings": findings,
        "document_length": len(document_text),
        "source": source
    }

@tool
def scan_prompt_template(
    template: str,
    template_name: str
) -> dict:
    """Audita un template de prompt antes de desplegarlo."""
    issues = []

    # Verificar que el template incluye defensas básicas
    if "NUNCA" not in template and "NEVER" not in template:
        issues.append("WARN: template sin restricciones explícitas")

    if "instrucciones" not in template.lower() and \
       "instructions" not in template.lower():
        issues.append("WARN: template no menciona protección de instrucciones")

    # Verificar que no tiene placeholders que permitan inyección
    import string
    placeholders = [
        fn for _, fn, _, _ in string.Formatter().parse(template)
        if fn is not None
    ]
    for ph in placeholders:
        issues.append(
            f"INFO: placeholder '{{{ph}}}' detectado. "
            f"Verificar que el contenido se valida antes de la inserción."
        )

    return {
        "template_name": template_name,
        "issues": issues,
        "has_critical": any(i.startswith("CRIT") for i in issues),
        "placeholder_count": len(placeholders)
    }

# Configuración del agente
injection_scanner = Agent(
    model="claude-haiku-4-5",
    tools=[scan_document_for_injection, scan_prompt_template],
    system_prompt="Eres un agente de seguridad especializado en detectar "
                  "prompt injection en documentos y templates. Analiza el "
                  "contenido proporcionado y reporta hallazgos con severidad."
)
