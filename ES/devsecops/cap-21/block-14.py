# Extraído de: LibroDevSecOps/cap-21-policy-as-code.md
policy = generate_rego_policy(
    requirement=(
        "Los deployments deben tener resource limits definidos "
        "para CPU y memoria. Bloquear si faltan limits. "
        "Advertir si los limits de memoria superan 2Gi."
    ),
    domain="kubernetes"
)
