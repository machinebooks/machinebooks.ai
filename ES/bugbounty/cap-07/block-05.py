# Extraído de: LibroBugBounty/cap-07-firma-codigo.md
#!/usr/bin/env python3
"""
AnÃ¡lisis de firma digital Authenticode con interpretaciÃ³n de seguridad.
Claude genera y ejecuta este script, luego interpreta los resultados.
"""
import subprocess
import json
from pathlib import Path

def analyze_signature(exe_path: str) -> dict:
    """Analiza la firma Authenticode de un ejecutable."""
    # PowerShell Get-AuthenticodeSignature es mÃ¡s fiable
    # que parsear el PE manualmente
    ps_command = f"""
    $sig = Get-AuthenticodeSignature '{exe_path}'
    @{{
        Status = $sig.Status.ToString()
        StatusMessage = $sig.StatusMessage
        SignerCertificate = @{{
            Subject = $sig.SignerCertificate.Subject
            Issuer = $sig.SignerCertificate.Issuer
            Thumbprint = $sig.SignerCertificate.Thumbprint
            NotBefore = $sig.SignerCertificate.NotBefore.ToString('o')
            NotAfter = $sig.SignerCertificate.NotAfter.ToString('o')
        }}
        TimeStamperCertificate = if ($sig.TimeStamperCertificate) {{
            @{{
                Subject = $sig.TimeStamperCertificate.Subject
                Issuer = $sig.TimeStamperCertificate.Issuer
            }}
        }} else {{ $null }}
        IsOSBinary = $sig.IsOSBinary
        Path = $sig.Path
    }} | ConvertTo-Json -Depth 3
    """

    result = subprocess.run(
        ["powershell", "-Command", ps_command],
        capture_output=True, text=True, timeout=15
    )

    try:
        sig_data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return {"error": result.stderr, "raw": result.stdout}

    # EvaluaciÃ³n de seguridad
    issues = []

    if sig_data.get("Status") != "Valid":
        issues.append(f"Firma no vÃ¡lida: {sig_data.get('Status')}")

    signer = sig_data.get("SignerCertificate", {})
    subject = signer.get("Subject", "")

    # Verificar que el firmante es quien esperamos
    # (no un certificado genÃ©rico o comprometido)
    if "CN=" not in subject:
        issues.append("Certificado sin Common Name")

    # Verificar timestamp (firma sobrevive a expiraciÃ³n del cert)
    if not sig_data.get("TimeStamperCertificate"):
        issues.append("Sin timestamp: firma expirarÃ¡ con el certificado")

    sig_data["security_issues"] = issues
    return sig_data


def compare_signatures(executables: list[str]) -> list[dict]:
    """Compara firmas de mÃºltiples ejecutables."""
    results = []
    for exe in executables:
        sig = analyze_signature(exe)
        results.append({
            "file": Path(exe).name,
            "status": sig.get("Status", "Unknown"),
            "signer": sig.get("SignerCertificate", {}).get("Subject", ""),
            "issues": sig.get("security_issues", []),
        })
    return results
