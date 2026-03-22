# Source: The DevSecOps and the Machine -- Chapter 11
# Pattern: OPA exclusion policies for auto-remediation

# policies/remediation/exclusions.rego
package remediation.exclusions

# Authentication files: never auto-fix
excluded[msg] {
    auth_patterns := [
        "auth", "login", "oauth", "jwt",
        "session", "token_verify", "permissions"
    ]
    pattern := auth_patterns[_]
    contains(lower(input.file_path), pattern)
    msg := sprintf(
        "File %s contains authentication logic: "
        "requires human review",
        [input.file_path]
    )
}

# Files marked as security-critical
excluded[msg] {
    input.file_annotations[_] == "@security-critical"
    msg := sprintf(
        "File %s marked as @security-critical",
        [input.file_path]
    )
}

# Changes exceeding 50 lines
excluded[msg] {
    input.estimated_lines_changed > 50
    msg := sprintf(
        "Fix estimated at %d lines (maximum allowed: 50)",
        [input.estimated_lines_changed]
    )
}

# Findings without test coverage
excluded[msg] {
    input.test_coverage_percent < 30
    msg := sprintf(
        "File test coverage: %d%% "
        "(minimum required: 30%%)",
        [input.test_coverage_percent]
    )
}

# Services in payment path
excluded[msg] {
    input.service_tags[_] == "payment-critical"
    msg := sprintf(
        "Service %s in payment path: requires human review",
        [input.service_name]
    )
}