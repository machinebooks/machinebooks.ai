# Extraído de: LibroUsuario/cap-21-la-nube-desde-el-cli.md
# Apagar desarrollo a las 20:00 L-V
0 20 * * 1-5 /opt/scripts/cloud-scheduler.sh stop >> /var/log/cloud-scheduler.log 2>&1
# Encender desarrollo a las 8:00 L-V
0 8 * * 1-5 /opt/scripts/cloud-scheduler.sh start >> /var/log/cloud-scheduler.log 2>&1
