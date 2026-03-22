# Extraído de: LibroUsuario/cap-22-contenedores-y-despliegues.md
docker compose up -d --scale worker=4

# Verificar
docker compose ps --format "table {{.Name}}\t{{.Status}}" | grep worker
