# Extraído de: LibroDevSecOps/cap-21-policy-as-code.md
# policies/kubernetes/network_policy.rego
package kubernetes.network_policy

import future.keywords.in
import future.keywords.if
import future.keywords.contains

# Denegar servicios de tipo LoadBalancer sin anotación de restricción
deny contains msg if {
    input.kind == "Service"
    input.spec.type == "LoadBalancer"
    not input.metadata.annotations["security/approved-external"]
    msg := sprintf(
        "El servicio '%s' usa LoadBalancer sin aprobación explícita. "
        + "Añada la anotación security/approved-external.",
        [input.metadata.name]
    )
}

# Denegar namespaces sin NetworkPolicy default-deny
deny contains msg if {
    input.kind == "Namespace"
    namespace_name := input.metadata.name
    not has_default_deny_policy(namespace_name)
    msg := sprintf(
        "El namespace '%s' no tiene NetworkPolicy default-deny asociada",
        [namespace_name]
    )
}

has_default_deny_policy(ns) if {
    some policy in data.network_policies
    policy.metadata.namespace == ns
    policy.spec.policyTypes[_] == "Ingress"
    count(policy.spec.ingress) == 0
}
