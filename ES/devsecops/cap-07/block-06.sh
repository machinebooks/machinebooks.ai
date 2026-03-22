# Extraído de: LibroDevSecOps/cap-07-contenedores.md
# Escaneo de configuración del Dockerfile
trivy config --format json --output trivy-config.json \
  --severity HIGH,CRITICAL \
  ./Dockerfile
