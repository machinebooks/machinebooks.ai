# Extraído de: LibroDevSecOps/cap-05-sca-sbom.md
# scripts/rescan_all_sboms.py
"""
Re-escanea todos los SBOMs almacenados cuando se publica una nueva CVE.
Descarga artefactos del pipeline y ejecuta Grype actualizado.
"""
import subprocess
import json
import os
import anthropic

def rescan_sbom(sbom_path: str) -> dict:
    """Ejecuta Grype contra un SBOM con base de datos actualizada."""
    # Actualizar base de datos de Grype
    subprocess.run(["grype", "db", "update"], check=True)

    result = subprocess.run(
        ["grype", f"sbom:{sbom_path}", "-o", "json"],
        capture_output=True, text=True
    )
    return json.loads(result.stdout)

def check_new_cve(vulns: dict, cve_id: str) -> list:
    """Filtra hallazgos que coinciden con la CVE nueva."""
    return [
        m for m in vulns.get("matches", [])
        if m["vulnerability"]["id"] == cve_id
    ]

def notify_affected_services(affected: list, cve_id: str):
    """Genera informe de impacto con Claude y notifica."""
    if not affected:
        print(f"CVE {cve_id}: ningún servicio afectado.")
        return

    client = anthropic.Anthropic()
    context = json.dumps(affected, indent=2, ensure_ascii=False)

    message = client.messages.create(
        model="claude-haiku-4-5",  # Haiku para notificaciones rápidas
        max_tokens=512,
        system="Resume el impacto de esta CVE en los servicios afectados. "
               "Incluye: servicios, versiones y acción recomendada. Formato Markdown.",
        messages=[{"role": "user", "content": f"CVE: {cve_id}\n\nServicios afectados:\n{context}"}]
    )

    print(f"## Impacto de {cve_id}\n")
    print(message.content[0].text)
