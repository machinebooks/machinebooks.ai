// Extraído de: LibroBugBounty/cap-13-vm-escape-rpc.md
LONG WinVerifyTrust(
    HWND   hwnd,           // Handle de ventana (puede ser INVALID_HANDLE_VALUE)
    GUID   *pgActionID,    // GUID de la acción de verificación
    LPVOID pWVTData        // Estructura WINTRUST_DATA con path del fichero
);
