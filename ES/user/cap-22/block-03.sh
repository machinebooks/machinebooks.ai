# Extraído de: LibroUsuario/cap-22-contenedores-y-despliegues.md
# Comprobar que nginx responde
curl -s -o /dev/null -w "%{http_code}" http://localhost:80/health

# Comprobar que la API responde a través de nginx
curl -s -o /dev/null -w "%{http_code}" http://localhost:80/api/v1/health

# Comprobar que Meilisearch responde
curl -s -o /dev/null -w "%{http_code}" http://localhost:7700/health
