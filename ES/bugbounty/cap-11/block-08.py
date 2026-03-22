# Extraído de: LibroBugBounty/cap-11-kernel-rw.md
# PASO 1: Mapear la primera página de memoria física
# Buscar la dirección del EPROCESS del proceso SYSTEM (PID 4)
phys_scan_addr = 0x1000
phys_scan_size = 0x10000000  # 256 MB de escaneo

# PASO 2: En memoria física, buscar la estructura EPROCESS
# con UniqueProcessId = 4 (SYSTEM)
# El offset de UniqueProcessId en EPROCESS varía por versión de Windows:
#   Windows 10 21H2: offset 0x440
#   Windows 11 23H2: offset 0x440

# PASO 3: Leer el token de SYSTEM desde EPROCESS
# Offset de Token en EPROCESS: 0x4B8 (Windows 11)
# El token es un _EX_FAST_REF que incluye 4 bits de referencia

# PASO 4: Encontrar el EPROCESS de nuestro proceso (PID actual)
# Buscar en la lista enlazada ActiveProcessLinks

# PASO 5: Copiar el token de SYSTEM al token de nuestro proceso
# Después de esto, nuestro proceso tiene privilegios de SYSTEM

# PASO 6: Spawn cmd.exe — ahora como NT AUTHORITY\SYSTEM
