# Extraído de: LibroDevSecOps/cap-07-contenedores.md
# Escaneo de imagen con salida JSON para el agente
trivy image --format json --output trivy-results.json \
  --severity HIGH,CRITICAL \
  mi-app:latest
