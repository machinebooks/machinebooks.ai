# Extraído de: LibroDevSecOps/cap-21-policy-as-code.md
# tests/kubernetes/container_security_test.rego
package kubernetes.container_security_test

import data.kubernetes.container_security

# Test: contenedor con runAsNonRoot pasa la política
test_non_root_allowed if {
    count(container_security.deny) == 0 with input as {
        "kind": "Pod",
        "spec": {"containers": [{
            "name": "api",
            "image": "ghcr.io/nuestra-org/api:v1.2",
            "securityContext": {
                "runAsNonRoot": true,
                "privileged": false
            }
        }]}
    }
    with data.approved_registries as ["ghcr.io/nuestra-org/"]
}

# Test: contenedor como root es denegado
test_root_denied if {
    count(container_security.deny) > 0 with input as {
        "kind": "Pod",
        "spec": {"containers": [{
            "name": "api",
            "image": "ghcr.io/nuestra-org/api:v1.2",
            "securityContext": {"privileged": false}
        }]}
    }
    with data.approved_registries as ["ghcr.io/nuestra-org/"]
}

# Test: imagen de registro no aprobado es denegada
test_unapproved_registry_denied if {
    count(container_security.deny) > 0 with input as {
        "kind": "Pod",
        "spec": {"containers": [{
            "name": "api",
            "image": "docker.io/random/image:latest",
            "securityContext": {
                "runAsNonRoot": true,
                "privileged": false
            }
        }]}
    }
    with data.approved_registries as ["ghcr.io/nuestra-org/"]
}
