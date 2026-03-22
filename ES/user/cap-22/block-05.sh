# Extraído de: LibroUsuario/cap-22-contenedores-y-despliegues.md
docker stats --no-stream --format \
  "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
