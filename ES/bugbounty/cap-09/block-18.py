# Extraído de: LibroBugBounty/cap-09-ioctl-fuzzing.md
import subprocess

def enable_driver_verifier(driver_name):
    """Activa Driver Verifier para el driver target."""
    # Activar verificaciones: pool tracking, IRQL checking,
    # deadlock detection, security checks
    subprocess.run([
        "verifier", "/flags", "0x9BB",
        "/driver", driver_name
    ], check=True)
    print(f"[*] Driver Verifier enabled for {driver_name}")
    print("[!] System MUST be rebooted for changes to take effect")
    print("[!] Run fuzzing in a VM — Verifier increases BSOD probability")

def check_verifier_log():
    """Revisa si Driver Verifier detectó violaciones."""
    result = subprocess.run(
        ["verifier", "/query"],
        capture_output=True, text=True
    )
    if "Current" in result.stdout:
        print("[*] Driver Verifier active")
    # Buscar violaciones en event log
    violations = subprocess.run([
        "wevtutil", "qe", "System",
        "/q:*[System[Provider[@Name='Driver Verifier']]]",
        "/f:text", "/c:20"
    ], capture_output=True, text=True)
    return violations.stdout
