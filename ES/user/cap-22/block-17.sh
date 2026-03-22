# Extraído de: LibroUsuario/cap-22-contenedores-y-despliegues.md
# Verificar pods nuevos
kubectl get pods -n production -l app=api-server \
  -o custom-columns="NAME:.metadata.name,STATUS:.status.phase,\
READY:.status.containerStatuses[0].ready,\
IMAGE:.spec.containers[0].image"

# Verificar que el endpoint responde
kubectl exec -n production \
  $(kubectl get pod -n production -l app=api-server -o jsonpath='{.items[0].metadata.name}') \
  -- curl -s http://localhost:8080/health

# Ver eventos recientes
kubectl get events -n production \
  --sort-by=.metadata.creationTimestamp | tail -10
