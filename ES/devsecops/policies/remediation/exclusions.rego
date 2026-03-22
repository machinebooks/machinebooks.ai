# Extraído de: LibroDevSecOps/cap-11-remediacion-automatica.md
# policies/remediation/exclusions.rego
package remediation.exclusions

# Ficheros de autenticación: nunca auto-fix
excluded[msg] {
    auth_patterns := [
        "auth", "login", "oauth", "jwt",
        "session", "token_verify", "permissions"
    ]
    pattern := auth_patterns[_]
    contains(lower(input.file_path), pattern)
    msg := sprintf(
        "Fichero %s contiene lógica de autenticación: "
        "requiere revisión humana",
        [input.file_path]
    )
}

# Ficheros marcados como security-critical
excluded[msg] {
    input.file_annotations[_] == "@security-critical"
    msg := sprintf(
        "Fichero %s marcado como @security-critical",
        [input.file_path]
    )
}

# Cambios que superan 50 líneas
excluded[msg] {
    input.estimated_lines_changed > 50
    msg := sprintf(
        "Fix estimado en %d líneas (máximo permitido: 50)",
        [input.estimated_lines_changed]
    )
}

# Hallazgos sin cobertura de tests
excluded[msg] {
    input.test_coverage_percent < 30
    msg := sprintf(
        "Cobertura de tests del fichero: %d%% "
        "(mínimo requerido: 30%%)",
        [input.test_coverage_percent]
    )
}

# Servicios en path de pago
excluded[msg] {
    input.service_tags[_] == "payment-critical"
    msg := sprintf(
        "Servicio %s en path de pago: requiere revisión humana",
        [input.service_name]
    )
}
