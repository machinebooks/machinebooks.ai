# Source: The DevSecOps and the Machine -- Chapter 9
# Pattern: OPA mandatory triage rules (PCI-DSS, exploits)

# policies/triage/mandatory_rules.rego
package triage.mandatory

# Every CVE with CVSS >= 9.0 in a PCI-DSS service is immediate action
force_immediate[msg] {
    input.cvss_score >= 9.0
    input.compliance_scope[_] == "pci-dss"
    msg := sprintf(
        "CVE %s (CVSS %v) in PCI-DSS service: mandatory immediate action",
        [input.cve_id, input.cvss_score]
    )
}

# Every CVE with a public exploit in an internet-facing service is immediate action
force_immediate[msg] {
    input.exploit_public == true
    input.internet_facing == true
    msg := sprintf(
        "CVE %s with public exploit in exposed service: immediate action",
        [input.cve_id]
    )
}

# Findings in services with restricted data never go to backlog
deny_backlog[msg] {
    input.data_classification == "restricted"
    msg := sprintf(
        "Finding %s in service with restricted data: minimum planned action",
        [input.finding_id]
    )
}