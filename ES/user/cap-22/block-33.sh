# Extraído de: LibroUsuario/cap-22-contenedores-y-despliegues.md
docker compose logs --since 2h api-backend 2>&1 | grep -i "error\|exception\|failed"
