# Extraído de: LibroTecnico/cap-21-cicd.md
# Configuración del usuario de despliegue en el servidor
# (ejecutar una vez manualmente, no parte del pipeline)

# Crear usuario con shell restringida
useradd -m -s /bin/bash deploy

# Dar al usuario acceso al grupo docker (para ejecutar docker compose)
usermod -aG docker deploy

# Crear directorio del proyecto con permisos correctos
mkdir -p /opt/plataforma
chown deploy:deploy /opt/plataforma

# Configurar la clave SSH autorizada
mkdir -p /home/deploy/.ssh
echo "CLAVE_PUBLICA_SSH_DEPLOY" >> /home/deploy/.ssh/authorized_keys
chmod 700 /home/deploy/.ssh
chmod 600 /home/deploy/.ssh/authorized_keys
chown -R deploy:deploy /home/deploy/.ssh
