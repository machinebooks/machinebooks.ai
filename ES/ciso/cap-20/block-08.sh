# Extraído de: LibroCISO/cap-20-docker-compose.md
# Permisos del fichero .env.prod en el servidor
chmod 600 .env.prod     # Solo lectura por el propietario
chown root:root .env.prod
