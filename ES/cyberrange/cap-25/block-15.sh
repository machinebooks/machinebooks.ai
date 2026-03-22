# Extraído de: LibroCyberrange/cap-25-despliegue-produccion.md
# Ejemplo didáctico: patrones/deploy/deploy-production.sh

#!/bin/bash
set -euo pipefail

# 1. Verificar que .env existe y tiene las claves requeridas
if [ ! -f .env ]; then
    echo "ERROR: Fichero .env no encontrado. Copiar de .env.example y configurar."
    exit 1
fi

# 2. Verificar conectividad con Proxmox
if ! curl -sk "https://${PROXMOX_HOST}:${PROXMOX_PORT}/api2/json/version" > /dev/null 2>&1; then
    echo "AVISO: Proxmox no accesible en ${PROXMOX_HOST}:${PROXMOX_PORT}"
fi

# 3. Construir imágenes
docker compose -f docker-compose.yml -f docker-compose.prod.yml build

# 4. Parar servicios anteriores sin destruir volúmenes
docker compose -f docker-compose.yml -f docker-compose.prod.yml down

# 5. Levantar servicios
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 6. Esperar a que MySQL esté healthy
echo "Esperando a MySQL..."
until docker compose exec db mysqladmin ping -h localhost --silent 2>/dev/null; do
    sleep 2
done
echo "MySQL listo."

# 7. Verificar que el backend responde
echo "Verificando backend..."
until curl -sf http://localhost:${BACKEND_PORT:-18000}/ping > /dev/null 2>&1; do
    sleep 2
done
echo "Backend operativo."

# 8. Mostrar estado final
docker compose -f docker-compose.yml -f docker-compose.prod.yml ps
