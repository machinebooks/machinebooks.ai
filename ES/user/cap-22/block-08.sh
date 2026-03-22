# Extraído de: LibroUsuario/cap-22-contenedores-y-despliegues.md
cd /opt/staging/

# Estado actual del contenedor
docker compose ps api-backend

# Logs de las últimas 5 reintentos
docker compose logs --tail=100 api-backend

# Inspeccionar el contenedor para ver la configuración
docker inspect staging-api-backend-1 | \
  jq '.[0] | {State, Config: {Env: .Config.Env, Cmd: .Config.Cmd},
    HostConfig: {Memory: .HostConfig.Memory}}'

# Verificar si el problema es de red (conectividad a otros servicios)
docker compose exec api-backend ping -c 1 postgres 2>/dev/null || \
  echo "No se puede conectar a postgres desde api-backend"
