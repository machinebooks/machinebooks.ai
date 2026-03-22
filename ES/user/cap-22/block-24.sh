# Extraído de: LibroUsuario/cap-22-contenedores-y-despliegues.md
# Actualizar el secret (codificado en base64 automáticamente)
kubectl create secret generic api-credentials \
  -n production \
  --from-literal=DATABASE_PASSWORD='<TU_NUEVA_CONTRASEÑA>' \
  --dry-run=client -o yaml | kubectl apply -f -

# Reiniciar los pods para que lean el nuevo secret
kubectl rollout restart deployment/api-server -n production

# Verificar que los pods nuevos arrancan correctamente
kubectl rollout status deployment/api-server -n production --timeout=60s
