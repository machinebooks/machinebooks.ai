# Extraído de: LibroDevSecOps/cap-07-contenedores.md
# Escaneo del filesystem (dependencias + IaC)
trivy fs --format json --output trivy-fs.json \
  --severity HIGH,CRITICAL \
  --scanners vuln,misconfig \
  .
