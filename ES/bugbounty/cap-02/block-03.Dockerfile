# Extraído de: LibroBugBounty/cap-02-stack-hunter.md
# Paquetes de sistema: reversing, networking, anÃ¡lisis
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Build essentials + compilaciÃ³n cruzada Windows
    build-essential gcc g++ make cmake \
    mingw-w64 gcc-mingw-w64-x86-64 g++-mingw-w64-x86-64 \
    # Reversing y anÃ¡lisis binario
    binutils file xxd \
    # Herramientas de red
    tcpdump nmap netcat-openbsd iproute2 iputils-ping dnsutils \
    tshark wireshark-common \
    # CompresiÃ³n
    p7zip-full unzip \
    # Utilidades
    git curl wget jq vim less tree \
    # Dependencias de anÃ¡lisis PE
    libmagic1 libfuzzy-dev ssdeep \
    # Cripto
    libssl-dev libffi-dev \
    && rm -rf /var/lib/apt/lists/*
