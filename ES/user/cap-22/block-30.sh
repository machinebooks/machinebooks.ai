# Extraído de: LibroUsuario/cap-22-contenedores-y-despliegues.md
# Espacio ocupado
docker system df

# Limpieza segura (solo recursos no utilizados)
docker system prune -f --volumes
docker image prune -a -f --filter "until=720h"  # Imágenes > 30 días
