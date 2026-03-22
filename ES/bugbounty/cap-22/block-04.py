# Extraído de: LibroBugBounty/cap-22-caso-asus.md
import ctypes
import ctypes.wintypes as wt

kernel32 = ctypes.windll.kernel32

# Intentar abrir el dispositivo (usuario estandar)
h = kernel32.CreateFileW(
    r"\\.\Asusgio3",
    0xC0000000,  # GENERIC_READ | GENERIC_WRITE
    0, None, 3, 0x80, None
)
err = kernel32.GetLastError()
# Resultado: ACCESS_DENIED (error 5)
# El dispositivo EXISTE pero la DACL bloquea
