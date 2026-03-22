# Extraído de: LibroBugBounty/cap-02-stack-hunter.md
# Paquetes Python de seguridad y reversing
RUN pip install --no-cache-dir \
    # SMB / Protocolos de red
    impacket scapy \
    # AnÃ¡lisis binario
    capstone unicorn keystone-engine lief pefile \
    # Fuzzing
    boofuzz \
    # Cripto y hashing
    pycryptodome \
    # Formato y salida
    rich tabulate hexdump \
    # PE/driver analysis
    yara-python ssdeep \
    # Dev
    ipython
