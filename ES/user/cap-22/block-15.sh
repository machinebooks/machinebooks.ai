# Extraído de: LibroUsuario/cap-22-contenedores-y-despliegues.md
# Configurar la estrategia de actualización
kubectl patch deployment api-server -n production -p '{
  "spec": {
    "strategy": {
      "type": "RollingUpdate",
      "rollingUpdate": {
        "maxUnavailable": 0,
        "maxSurge": 1
      }
    },
    "minReadySeconds": 10,
    "progressDeadlineSeconds": 120
  }
}'

# Actualizar la imagen
kubectl set image deployment/api-server \
  api-server=registry.ejemplo.com/api-server:2.5.0 \
  -n production

# Anotar el motivo del despliegue (para auditoría)
kubectl annotate deployment api-server -n production \
  kubernetes.io/change-cause="Deploy v2.5.0 - ticket OPS-1234" \
  --overwrite

# Monitorizar el progreso
kubectl rollout status deployment/api-server -n production --timeout=180s
