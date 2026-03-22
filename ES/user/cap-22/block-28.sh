# Extraído de: LibroUsuario/cap-22-contenedores-y-despliegues.md
# Verificar DNS
nslookup api-externo.ejemplo.com

# Verificar conectividad TCP
nc -zv api-externo.ejemplo.com 443

# Verificar variables de entorno
env | grep -i "api\|url\|host\|port"

# Verificar certificados SSL
openssl s_client -connect api-externo.ejemplo.com:443 -brief
