# Extraído de: LibroDevSecOps/cap-29-futuro-seguridad-autonoma.md
# adaptive_defense_policy.rego — Política adaptativa para nivel de amenaza
# Se evalúa en cada ciclo del pipeline para ajustar umbrales
package adaptive_security

import future.keywords.if

# Nivel de amenaza basado en indicadores externos
threat_level := "elevated" if {
    # CVE crítica publicada en últimas 24h para tecnologías del stack
    input.cve_feed.critical_last_24h > 0
    input.cve_feed.affects_our_stack == true
}

threat_level := "elevated" if {
    # Incremento anómalo de intentos de acceso al repositorio
    input.github_audit.failed_auth_last_hour > 10
}

threat_level := "normal" if {
    not threat_level == "elevated"
}

# Ajuste dinámico de niveles de autonomía según amenaza
max_autonomy_level := 2 if {
    threat_level == "elevated"
}

max_autonomy_level := 1 if {
    threat_level == "normal"
}

# Bajo amenaza elevada, todo sube un nivel de supervisión
deny[msg] if {
    threat_level == "elevated"
    input.finding.proposed_autonomy == 1
    msg := "Amenaza elevada: hallazgo reclasificado a nivel 2 (supervisado)"
}
