# Extraído de: LibroBugBounty/cap-06-dll-sideloading.md
# Compilar la proxy DLL en el contenedor
docker exec aegis-security-lab \
    x86_64-w64-mingw32-gcc -shared \
    -o /lab/results/VERSION.dll \
    /lab/scripts/proxy_version.c \
    -Wl,--enable-stdcall-fixup
