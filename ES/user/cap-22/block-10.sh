# Extraído de: LibroUsuario/cap-22-contenedores-y-despliegues.md
# Comprobar si la base de datos existe
docker compose exec postgres psql -U postgres -c "\l" | grep staging_db

# Comprobar si el usuario existe
docker compose exec postgres psql -U postgres -c "\du" | grep app
