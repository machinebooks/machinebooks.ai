# Extraído de: LibroBugBounty/cap-11-kernel-rw.md
def virt_to_phys(phys_memory, cr3, virt_addr):
    """Traduce dirección virtual a física via tablas de páginas."""
    # CR3 contiene la dirección física del PML4
    pml4_phys = cr3 & ~0xFFF

    # Nivel 4: PML4 Entry
    pml4_idx = (virt_addr >> 39) & 0x1FF
    pml4e = phys_memory.read_qword(pml4_phys + pml4_idx * 8)
    if not (pml4e & 1):  # Present bit
        return None

    # Nivel 3: PDPT Entry
    pdpt_phys = pml4e & 0x000FFFFFFFFFF000
    pdpt_idx = (virt_addr >> 30) & 0x1FF
    pdpte = phys_memory.read_qword(pdpt_phys + pdpt_idx * 8)
    if not (pdpte & 1):
        return None
    if pdpte & 0x80:  # 1 GB huge page
        return (pdpte & 0x000FFFFFC0000000) | (virt_addr & 0x3FFFFFFF)

    # Nivel 2: PD Entry
    pd_phys = pdpte & 0x000FFFFFFFFFF000
    pd_idx = (virt_addr >> 21) & 0x1FF
    pde = phys_memory.read_qword(pd_phys + pd_idx * 8)
    if not (pde & 1):
        return None
    if pde & 0x80:  # 2 MB large page
        return (pde & 0x000FFFFFFFE00000) | (virt_addr & 0x1FFFFF)

    # Nivel 1: PT Entry
    pt_phys = pde & 0x000FFFFFFFFFF000
    pt_idx = (virt_addr >> 12) & 0x1FF
    pte = phys_memory.read_qword(pt_phys + pt_idx * 8)
    if not (pte & 1):
        return None

    # Dirección física final
    return (pte & 0x000FFFFFFFFFF000) | (virt_addr & 0xFFF)
