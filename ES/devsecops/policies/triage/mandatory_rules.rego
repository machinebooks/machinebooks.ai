# Extraído de: LibroDevSecOps/cap-09-agente-triaje.md
# policies/triage/mandatory_rules.rego
package triage.mandatory

# Toda CVE con CVSS >= 9.0 en servicio PCI-DSS es acción inmediata
force_immediate[msg] {
    input.cvss_score >= 9.0
    input.compliance_scope[_] == "pci-dss"
    msg := sprintf(
        "CVE %s (CVSS %v) en servicio PCI-DSS: acción inmediata obligatoria",
        [input.cve_id, input.cvss_score]
    )
}

# Toda CVE con exploit público en servicio internet-facing es acción inmediata
force_immediate[msg] {
    input.exploit_public == true
    input.internet_facing == true
    msg := sprintf(
        "CVE %s con exploit público en servicio expuesto: acción inmediata",
        [input.cve_id]
    )
}

# Hallazgos en servicio con datos restringidos nunca van a backlog
deny_backlog[msg] {
    input.data_classification == "restricted"
    msg := sprintf(
        "Hallazgo %s en servicio con datos restringidos: mínimo acción planificada",
        [input.finding_id]
    )
}
