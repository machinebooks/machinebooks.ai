# Extraído de: LibroDevSecOps/cap-18-runtime-security.md
# Simular shell interactivo en contenedor (debe activar regla)
docker exec -it inference-service /bin/bash

# Simular escritura en directorio de sistema
docker exec inference-service \
    touch /usr/bin/backdoor 2>/dev/null

# Simular conexión a puerto no estándar
docker exec inference-service \
    python3 -c "import socket; s=socket.socket(); \
    s.connect(('10.0.0.1', 4444))" 2>/dev/null

# Verificar que las alertas se generaron
curl -s http://localhost:8765/healthz
# Revisar logs de Falco para confirmar alertas
docker logs falco --since 60s | grep -c "Warning\|Critical"
