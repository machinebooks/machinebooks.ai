# Source: The DevSecOps and the Machine -- Chapter 21
# Pattern: OPA policies for Kubernetes, deployments, and AI models

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

# policies/ai/model_approval.rego
package ai.model_approval

import future.keywords.in
import future.keywords.if
import future.keywords.contains

# Modelos aprobados para producción
approved_models := data.approved_models

# Clasificaciones de datos que permiten uso de LLM externo
external_llm_allowed := ["public", "internal"]

# Denegar uso de modelos no aprobados
deny contains msg if {
    model := input.model_id
    not model in approved_models
    msg := sprintf(
        "Modelo '%s' no está aprobado para producción. "
        + "Modelos permitidos: %v",
        [model, approved_models]
    )
}

# Denegar envío de datos confidenciales a LLM externo
deny contains msg if {
    input.data_classification == "confidential"
    input.llm_provider == "external"
    msg := sprintf(
        "Datos con clasificación '%s' no pueden enviarse a LLM externo. "
        + "Use un modelo local (Ollama) o anonimice los datos.",
        [input.data_classification]
    )
}

# Denegar envío de datos restringidos a cualquier LLM
deny contains msg if {
    input.data_classification == "restricted"
    msg := "Datos con clasificación 'restricted' no pueden procesarse con LLM"
}

# Advisory: consumo de tokens elevado
warn contains msg if {
    input.estimated_tokens > 50000
    msg := sprintf(
        "Operación con %d tokens estimados. "
        + "Considere prompt caching o model routing a claude-haiku-4-5.",
        [input.estimated_tokens]
    )
}