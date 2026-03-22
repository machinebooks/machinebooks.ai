# Extraído de: LibroBugBounty/cap-17-poc-impacto.md
import subprocess
import datetime

def capture_evidence(exploit_name):
    """Captura evidencia después de ejecutar un exploit."""
    evidence = {
        "exploit": exploit_name,
        "timestamp": datetime.datetime.now().isoformat(),
        "hostname": subprocess.getoutput("hostname"),
        "username": subprocess.getoutput("whoami"),
    }

    # Capturar screenshot (requiere Pillow o similar)
    try:
        import mss
        with mss.mss() as sct:
            filename = f"evidence_{exploit_name}.png"
            sct.shot(output=filename)
            evidence["screenshot"] = filename
    except ImportError:
        evidence["screenshot"] = "mss not installed"

    # Capturar proceso list relevante
    evidence["processes"] = subprocess.getoutput(
        "tasklist /fi \"imagename eq calc.exe\" /v"
    )

    # Capturar fichero de prueba si existe
    proof_file = f"C:\\Users\\Public\\{exploit_name}_proof.txt"
    try:
        with open(proof_file) as f:
            evidence["proof_content"] = f.read()
    except FileNotFoundError:
        evidence["proof_content"] = "Not found"

    return evidence
