# Extraído de: LibroPQC/cap-21-docker.md
# Arrancar todos los servicios
docker compose up -d

# Ver el estado de todos los servicios con healthcheck
docker compose ps

# Ver logs de un servicio específico (últimas 100 líneas, seguir)
docker compose logs -f --tail=100 pqc_backend

# Reiniciar solo el backend sin afectar a los demás servicios
docker compose restart pqc_backend

# Reconstruir la imagen del backend tras cambios en Dockerfile
docker compose build pqc_backend && docker compose up -d pqc_backend

# Ejecutar migraciones de base de datos dentro del contenedor
docker compose exec pqc_backend flask db upgrade

# Abrir una shell en el contenedor del backend para depuración
docker compose exec pqc_backend bash

# Parar todos los servicios (los volúmenes persisten)
docker compose down

# Parar y ELIMINAR volúmenes (DESTRUCTIVO: borra la base de datos)
docker compose down -v
