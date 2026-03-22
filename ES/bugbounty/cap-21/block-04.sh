# Extraído de: LibroBugBounty/cap-21-caso-steam.md
gcc -shared -m32 -o VERSION.dll steam_poc.c \
    -lkernel32 -ladvapi32
