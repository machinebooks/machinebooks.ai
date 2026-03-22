# Extraído de: LibroBugBounty/cap-02-stack-hunter.md
# Reconstruir la imagen cada dos semanas
docker-compose build --no-cache

# O actualizar solo radare2 (la herramienta que mÃ¡s evoluciona)
docker exec aegis-security-lab bash -c \
    "cd /tmp && git clone --depth=1 \
    https://github.com/radareorg/radare2.git && \
    cd radare2 && sys/install.sh"

# Actualizar paquetes Python
docker exec aegis-security-lab pip install --upgrade \
    pefile lief capstone r2pipe boofuzz
