# Extraído de: LibroUsuario/cap-22-contenedores-y-despliegues.md
# Rollback al despliegue anterior
kubectl rollout undo deployment/api-server -n production

# Monitorizar
kubectl rollout status deployment/api-server -n production --timeout=120s

# Verificar
kubectl get pods -n production -l app=api-server \
  -o custom-columns="NAME:.metadata.name,IMAGE:.spec.containers[0].image"
