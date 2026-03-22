# Extraído de: LibroBugBounty/cap-17-poc-impacto.md
# Compilación de DLL proxy (32-bit)
i686-w64-mingw32-gcc -shared -o VERSION.dll version_proxy.c -lkernel32

# IMPORTANTE: verificar la arquitectura del target
file target.exe
# target.exe: PE32 executable (GUI) Intel 80386 → usar i686
# target.exe: PE32+ executable (GUI) x86-64   → usar x86_64
