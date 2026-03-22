# Extraído de: LibroBugBounty/cap-17-poc-impacto.md
# Instalación de MinGW en Windows (via MSYS2)
pacman -S mingw-w64-x86_64-gcc

# Compilación de una DLL proxy (64-bit)
x86_64-w64-mingw32-gcc -shared -o VERSION.dll version_proxy.c -lkernel32

# Compilación de un payload de servicio (64-bit)
x86_64-w64-mingw32-gcc -o payload.exe payload_service.c -ladvapi32

# Compilación estática (sin dependencias de runtime)
x86_64-w64-mingw32-gcc -static -o exploit.exe exploit.c -ladvapi32
