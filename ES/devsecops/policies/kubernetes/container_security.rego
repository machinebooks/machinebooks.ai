# Extraído de: LibroDevSecOps/cap-21-policy-as-code.md
# policies/kubernetes/container_security.rego
package kubernetes.container_security

import future.keywords.in
import future.keywords.if
import future.keywords.contains

# Datos externos: lista de registros aprobados
approved_registries := data.approved_registries

# Denegar pods que ejecuten como root
deny contains msg if {
    input.kind == "Pod"
    some container in input.spec.containers
    not container.securityContext.runAsNonRoot
    msg := sprintf(
        "El contenedor '%s' debe definir runAsNonRoot: true",
        [container.name]
    )
}

# Denegar contenedores privilegiados
deny contains msg if {
    input.kind == "Pod"
    some container in input.spec.containers
    container.securityContext.privileged
    msg := sprintf(
        "El contenedor '%s' no puede ejecutarse en modo privilegiado",
        [container.name]
    )
}

# Denegar imágenes de registros no aprobados
deny contains msg if {
    input.kind == "Pod"
    some container in input.spec.containers
    image := container.image
    not image_from_approved_registry(image)
    msg := sprintf(
        "La imagen '%s' no pertenece a un registro aprobado: %v",
        [image, approved_registries]
    )
}

# Helper: verificar si la imagen usa un registro aprobado
image_from_approved_registry(image) if {
    some registry in approved_registries
    startswith(image, registry)
}
