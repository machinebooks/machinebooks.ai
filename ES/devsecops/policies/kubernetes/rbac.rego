# Extraído de: LibroDevSecOps/cap-21-policy-as-code.md
# policies/kubernetes/rbac.rego
package kubernetes.rbac

import future.keywords.in
import future.keywords.if
import future.keywords.contains

# Roles peligrosos que requieren aprobación explícita
dangerous_verbs := ["*", "delete", "exec", "escalate"]
dangerous_resources := ["secrets", "pods/exec", "clusterroles"]

# Denegar ClusterRoleBindings al grupo system:masters
deny contains msg if {
    input.kind == "ClusterRoleBinding"
    some subject in input.subjects
    subject.name == "system:masters"
    msg := "Prohibido crear ClusterRoleBinding al grupo system:masters"
}

# Alertar sobre roles con permisos excesivos
warn contains msg if {
    input.kind == "ClusterRole"
    some rule in input.rules
    some verb in rule.verbs
    verb in dangerous_verbs
    some resource in rule.resources
    resource in dangerous_resources
    msg := sprintf(
        "ClusterRole '%s' concede verbo '%s' sobre '%s'. "
        + "Requiere aprobación del equipo de seguridad.",
        [input.metadata.name, verb, resource]
    )
}
