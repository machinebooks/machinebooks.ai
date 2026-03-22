# Extraído de: LibroBugBounty/cap-03-etica-legalidad.md
#!/usr/bin/env python3
"""
Generador de report de vulnerabilidad con Claude.
Toma notas del investigador y produce un borrador estructurado.
"""
import anthropic

client = anthropic.Anthropic(api_key="<TU_API_KEY>")

def generate_report(notes: str, vendor: str, vuln_id: str) -> str:
    """Genera borrador de report desde notas del investigador."""
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{
            "role": "user",
            "content": f"""Genera un report de vulnerabilidad profesional
a partir de estas notas de investigaciÃ³n.

Vendor: {vendor}
ID: {vuln_id}

Notas del investigador:
{notes}

Requisitos:
- Formato Markdown con secciones: Executive Summary,
  Severity (CVSS v3.1), Affected Component, Technical Description,
  Steps to Reproduce, PoC, Impact, Remediation, Timeline
- Tono profesional y objetivo
- CVSS score con vector string completo
- CWE mapping
- Pasos de reproducciÃ³n numerados y especÃ­ficos
- Recomendaciones de remediaciÃ³n concretas
- NO incluir datos sensibles: IPs, tokens, credenciales reales"""
        }]
    )
    return message.content[0].text

# Ejemplo de uso (post-disclosure, ya seguro usar Claude)
notes = """
Discord VERSION.dll hijack.
El directorio de instalaciÃ³n (%LOCALAPPDATA%\\Discord) es
escribible por el usuario. Discord.exe carga VERSION.dll
desde su directorio antes de System32. Podemos poner una
proxy DLL que forwardea a la real y ejecuta payload.
PoC: DLL que spawns cmd.exe al cargar. PID confirmado.
ASLR y DEP activos pero irrelevantes (la DLL se carga
legÃ­timamente por la app). Afecta a Discord 1.0.9045+.
"""

report = generate_report(notes, "Discord", "DISCORD-2026-002")
print(report)
