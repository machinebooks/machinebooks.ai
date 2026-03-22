# Extraído de: LibroTecnico/cap-21-cicd.md
# Proceso de despliegue manual actual
# (documentado para comparación con el proceso automatizado)

# 1. Conectar al servidor de producción
ssh deploy@servidor-produccion

# 2. Navegar al directorio del proyecto
cd /opt/plataforma

# 3. Actualizar el código (si el servidor tiene acceso al repositorio)
git pull origin main

# 4. Reconstruir servicios modificados
# El arquitecto decide qué servicios han cambiado, manualmente
docker compose -f docker-compose.prod.yml build backend

# 5. Aplicar migraciones si las hay
docker compose -f docker-compose.prod.yml run --rm backend flask db upgrade

# 6. Reiniciar servicios
docker compose -f docker-compose.prod.yml up -d --no-deps backend

# 7. Verificar logs
docker compose -f docker-compose.prod.yml logs -f backend --tail=50

# 8. Verificar health check
curl http://localhost/api/health/full
