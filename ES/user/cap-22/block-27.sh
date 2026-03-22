# Extraído de: LibroUsuario/cap-22-contenedores-y-despliegues.md
# En Docker Compose
docker compose exec api-backend bash

# En Kubernetes (si el contenedor tiene shell)
kubectl exec -it -n production \
  $(kubectl get pod -n production -l app=api-server -o jsonpath='{.items[0].metadata.name}') \
  -- /bin/sh

# Si el contenedor no tiene shell (imagen minimal)
kubectl debug -it -n production <pod-name> \
  --image=busybox --target=api-server
