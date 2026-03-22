# Extraído de: LibroUsuario/cap-20-servidores-y-servicios.md
# Liberar caché del sistema (seguro, no afecta a servicios)
sync && echo 3 > /proc/sys/vm/drop_caches

# Reiniciar el servicio
sudo systemctl restart webapp

# Esperar 5 segundos y verificar
sleep 5
systemctl status webapp
curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health
