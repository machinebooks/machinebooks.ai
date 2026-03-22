# Extraído de: LibroUsuario/cap-22-contenedores-y-despliegues.md
# Escalar manualmente a 5
kubectl scale deployment/api-server -n production --replicas=5

# Configurar autoscaling
kubectl autoscale deployment api-server -n production \
  --min=3 --max=10 --cpu-percent=70

# Verificar
kubectl get hpa -n production
kubectl get pods -n production -l app=api-server
