# Extraído de: LibroBugBounty/cap-02-stack-hunter.md
# Instalar radare2 desde source (no estÃ¡ en repos de Bookworm)
RUN git clone --depth=1 https://github.com/radareorg/radare2.git /tmp/r2 && \
    cd /tmp/r2 && sys/install.sh && \
    rm -rf /tmp/r2

# r2pipe para scripting de radare2
RUN pip install --no-cache-dir r2pipe
