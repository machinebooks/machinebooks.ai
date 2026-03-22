# Extraído de: LibroDevSecOps/cap-21-policy-as-code.md
# policies/ai/data_classification.rego
package ai.data_classification

import future.keywords.if
import future.keywords.contains

# Reglas de retención por clasificación
max_retention_days := {
    "public": 365,
    "internal": 90,
    "confidential": 30,
    "restricted": 7,
}

# Denegar retención de logs LLM que exceda el máximo
deny contains msg if {
    classification := input.data_classification
    max_days := max_retention_days[classification]
    input.log_retention_days > max_days
    msg := sprintf(
        "Retención de %d días excede el máximo de %d para datos '%s'",
        [input.log_retention_days, max_days, classification]
    )
}

# Denegar operaciones sin clasificación de datos
deny contains msg if {
    not input.data_classification
    msg := "Toda operación LLM debe incluir clasificación de datos"
}
