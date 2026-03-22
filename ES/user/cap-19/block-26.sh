# Extraído de: LibroUsuario/cap-19-tu-terminal-potenciada.md
# Leer, modificar y mostrar sin sobreescribir todavía
jq '.database.host = "db-prod.ejemplo.com" | .cache.ttl = 3600' \
  /opt/app/config.json

# Si estás conforme, guardar:
jq '.database.host = "db-prod.ejemplo.com" | .cache.ttl = 3600' \
  /opt/app/config.json > /tmp/config_new.json && \
  mv /tmp/config_new.json /opt/app/config.json
