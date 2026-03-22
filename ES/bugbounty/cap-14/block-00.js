// Extraído de: LibroBugBounty/cap-14-extension-tampering.md
// Extraído del app.asar de Wand IDE
new BrowserWindow({
    webPreferences: {
        nodeIntegration: true,     // Código web puede usar Node.js APIs
        contextIsolation: false,   // No hay aislamiento entre contextos
        sandbox: false,            // Sin sandbox de Chromium
        enableRemoteModule: true,  // Módulo remote activado
    }
});
