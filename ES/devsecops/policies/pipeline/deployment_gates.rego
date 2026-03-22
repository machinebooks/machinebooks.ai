# Extraído de: LibroDevSecOps/cap-21-policy-as-code.md
# policies/pipeline/deployment_gates.rego
package pipeline.deployment_gates

import future.keywords.if
import future.keywords.contains

# Estructura esperada del input:
# {
#   "scan_results": { "critical": 0, "high": 2, "medium": 15 },
#   "tests": { "passed": 142, "failed": 0, "coverage": 78.5 },
#   "image_signed": true,
#   "sbom_generated": true,
#   "last_security_review_days": 12
# }

# Gate 1: cero vulnerabilidades críticas
deny contains msg if {
    input.scan_results.critical > 0
    msg := sprintf(
        "Despliegue bloqueado: %d vulnerabilidades críticas sin resolver",
        [input.scan_results.critical]
    )
}

# Gate 2: imagen firmada con cosign
deny contains msg if {
    not input.image_signed
    msg := "Despliegue bloqueado: la imagen no está firmada"
}

# Gate 3: SBOM generado y disponible
deny contains msg if {
    not input.sbom_generated
    msg := "Despliegue bloqueado: no se ha generado el SBOM"
}

# Gate 4: cobertura de tests mínima
deny contains msg if {
    input.tests.coverage < 70
    msg := sprintf(
        "Despliegue bloqueado: cobertura de tests %.1f%% (mínimo 70%%)",
        [input.tests.coverage]
    )
}

# Advisory: revisión de seguridad antigua
warn contains msg if {
    input.last_security_review_days > 30
    msg := sprintf(
        "Aviso: la última revisión de seguridad fue hace %d días",
        [input.last_security_review_days]
    )
}
