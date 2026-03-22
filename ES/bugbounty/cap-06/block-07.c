// Extraído de: LibroBugBounty/cap-06-dll-sideloading.md
// Defensas contra DLL sideloading en aplicaciones Windows

// 1. Cargar DLLs con ruta absoluta
// MAL:
HMODULE h = LoadLibrary("VERSION.dll");
// BIEN:
wchar_t sysdir[MAX_PATH];
GetSystemDirectoryW(sysdir, MAX_PATH);
wchar_t full_path[MAX_PATH];
swprintf(full_path, MAX_PATH, L"%s\\VERSION.dll", sysdir);
HMODULE h = LoadLibraryW(full_path);

// 2. Restringir directorios de bÃºsqueda
// Al inicio de la aplicaciÃ³n:
SetDefaultDllDirectories(LOAD_LIBRARY_SEARCH_SYSTEM32);
// Esto elimina el directorio de la app del orden de bÃºsqueda

// 3. Verificar firma digital de DLLs cargadas
// Antes de confiar en una DLL:
LONG lStatus;
WINTRUST_FILE_INFO FileData;
WINTRUST_DATA WinTrustData;
// ... (configurar estructuras)
lStatus = WinVerifyTrust(NULL, &WVTPolicyGUID, &WinTrustData);
if (lStatus != ERROR_SUCCESS) {
    // DLL no firmada o firma invÃ¡lida â€” no cargar
    FreeLibrary(h);
}

// 4. Instalar en Program Files
// El instalador DEBE usar %ProgramFiles%, no %LOCALAPPDATA%
// Esto requiere elevaciÃ³n (UAC) pero protege contra escritura
