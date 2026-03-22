# Extraído de: LibroUsuario/cap-22-contenedores-y-despliegues.md
# Estado actual del deployment
kubectl get deployment api-server -n production -o wide

# Pods actuales
kubectl get pods -n production -l app=api-server \
  -o custom-columns="NAME:.metadata.name,STATUS:.status.phase,\
READY:.status.containerStatuses[0].ready,\
RESTARTS:.status.containerStatuses[0].restartCount,\
AGE:.metadata.creationTimestamp"

# Versión actual de la imagen
kubectl get deployment api-server -n production \
  -o jsonpath='{.spec.template.spec.containers[0].image}'
