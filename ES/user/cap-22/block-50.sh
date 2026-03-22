# Extraído de: LibroUsuario/cap-22-contenedores-y-despliegues.md
# Verificar que ambos contenedores están en la misma red
docker network inspect staging_default | \
  jq '.[0].Containers | to_entries[] | {name: .value.Name, ip: .value.IPv4Address}'

# Verificar resolución DNS desde api-backend
docker compose exec api-backend nslookup redis

# Verificar conectividad TCP
docker compose exec api-backend nc -zv redis 6379

# Verificar que Redis está escuchando
docker compose exec redis redis-cli ping
