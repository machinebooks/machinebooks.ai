# Extraído de: LibroBugBounty/cap-20-caso-epic.md
x86_64-w64-mingw32-gcc -o EpicGamesUpdater_payload.exe \
    payload_service.c -lkernel32 -luser32 -ladvapi32 -O2 -s
