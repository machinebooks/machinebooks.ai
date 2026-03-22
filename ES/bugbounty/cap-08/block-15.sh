# Extraído de: LibroBugBounty/cap-08-analisis-drivers.md
# Iniciar radare2 con análisis completo
docker exec -it kernel-lab r2 -A /lab/drivers/AsIO3.sys

# Dentro de r2:
# 1. Verificar entry point (DriverEntry)
[0x00011000]> ie
# 2. Listar todas las funciones detectadas
[0x00011000]> afl
# 3. Buscar imports de ntoskrnl.exe
[0x00011000]> ii~ntoskrnl
# 4. Buscar cross-references a MmMapIoSpace
[0x00011000]> axt @sym.imp.MmMapIoSpace
# 5. Desensamblar la función que llama a MmMapIoSpace
[0x00011000]> pdf @ fcn.00011a30
