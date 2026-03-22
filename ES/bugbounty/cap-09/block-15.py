# Extraído de: LibroBugBounty/cap-09-ioctl-fuzzing.md
import subprocess

def monitor_during_fuzzing(duration_seconds=60):
    """Monitoriza indicadores de corrupción durante el fuzzing."""
    # 1. Pool integrity check (requiere driver verifier)
    subprocess.run(["verifier", "/query"], capture_output=True)

    # 2. Event log: buscar entradas del kernel
    subprocess.run([
        "wevtutil", "qe", "System",
        "/q:*[System[TimeCreated[@SystemTime>='2026-03-31T00:00:00']]]",
        "/f:text", "/c:50"
    ], capture_output=True)

    # 3. Pool tag statistics (buscar leaks)
    subprocess.run(["poolmon", "-b", "-n", "AsIO"], capture_output=True)
