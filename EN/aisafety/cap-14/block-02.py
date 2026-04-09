# Extracted from: LibroAISafety/ch-14-infrastructure.md
# Automatable security evaluation checklist for AI infrastructure
# Didactic code — real tests require specific tools

from dataclasses import dataclass
from enum import Enum

class Severity(Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Finding:
    component: str
    check: str
    severity: Severity
    description: str
    recommendation: str

def evaluate_electron(app_path: str) -> list[Finding]:
    """Security evaluation for Electron application."""
    findings = []

    # Check 1: ASAR integrity
    # Can it be extracted, modified, and repackaged without detection?
    findings.append(Finding(
        component="electron",
        check="asar_integrity",
        severity=Severity.HIGH,
        description="The ASAR has no integrity verification. "
                    "A local attacker can modify the application's code.",
        recommendation="Implement asar-integrity or hash verification at startup."
    ))

    # Check 2: Binary signing
    # Are executables and DLLs signed?
    findings.append(Finding(
        component="electron",
        check="binary_signing",
        severity=Severity.MEDIUM,
        description="Auxiliary binaries are not signed. "
                    "Susceptible to substitution.",
        recommendation="Sign all binaries with a code signing certificate."
    ))

    # Check 3: DLL search path
    # Does the application load DLLs from insecure locations?
    findings.append(Finding(
        component="electron",
        check="dll_search_path",
        severity=Severity.HIGH,
        description="The application searches for DLLs in the working directory "
                    "before system paths.",
        recommendation="Use SetDllDirectory or absolute paths for loading DLLs."
    ))

    return findings
