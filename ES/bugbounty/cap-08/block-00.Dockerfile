# Extraído de: LibroBugBounty/cap-08-analisis-drivers.md
FROM python:3.11-slim-bookworm

# Capa 1: herramientas del sistema (reversing, red, compilación cruzada)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential mingw-w64 gcc-mingw-w64-x86-64 \
    binutils file xxd \
    tcpdump nmap netcat-openbsd tshark \
    p7zip-full git curl wget jq vim less tree \
    libmagic1 libfuzzy-dev ssdeep libssl-dev libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Capa 2: paquetes Python para análisis de PE y fuzzing
RUN pip install --no-cache-dir \
    pefile lief capstone unicorn keystone-engine \
    boofuzz impacket scapy \
    rich tabulate hexdump yara-python r2pipe ipython

# Capa 3: radare2 desde fuente (no está en repos de Bookworm)
RUN git clone --depth=1 https://github.com/radareorg/radare2.git /tmp/r2 && \
    cd /tmp/r2 && sys/install.sh && rm -rf /tmp/r2
