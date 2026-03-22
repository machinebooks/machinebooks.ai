# Extraído de: LibroUsuario/cap-19-tu-terminal-potenciada.md
# Cambiar propietario
sudo chown -R www-data:www-data /var/www/app/

# Permisos estándar: 755 para directorios, 644 para ficheros
sudo find /var/www/app/ -type d -exec chmod 755 {} \;
sudo find /var/www/app/ -type f -exec chmod 644 {} \;

# Excepción: uploads con escritura de grupo
sudo chmod 775 /var/www/app/uploads/
sudo chgrp deploy /var/www/app/uploads/

# Proteger el fichero de configuración
sudo chmod 600 /var/www/app/.env
