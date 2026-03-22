# Extraído de: LibroUsuario/cap-22-contenedores-y-despliegues.md
cd /opt/staging/

# 1. Parar todo
docker compose down

# 2. Reconstruir imágenes específicas
docker compose build --no-cache api-backend worker

# 3. Levantar todo en segundo plano
docker compose up -d

# 4. Esperar a que los servicios arranquen
echo "Esperando 15 segundos para que los servicios inicialicen..."
sleep 15

# 5. Verificar estado
docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"
