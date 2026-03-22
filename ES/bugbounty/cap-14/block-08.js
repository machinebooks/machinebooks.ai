// Extraído de: LibroBugBounty/cap-14-extension-tampering.md
// Paso 1: Activar fuses de seguridad al compilar (electron-builder)
// En package.json o electron-builder.yml:
// "electronFuses": {
//   "RunAsNode": false,
//   "EnableNodeCliInspectArguments": false,
//   "OnlyLoadAppFromAsar": true,
//   "EnableEmbeddedAsarIntegrityValidation": true
// }

// Paso 2: Verificar integridad del ASAR en runtime (defensa adicional)
const crypto = require('crypto');
const fs = require('fs');

function verifyAsarIntegrity() {
    const asarPath = path.join(process.resourcesPath, 'app.asar');
    const asar = fs.readFileSync(asarPath);
    const hash = crypto.createHash('sha256').update(asar).digest('hex');

    // El hash de referencia debe venir de una fuente externa
    // NO del ejecutable (Wand's mistake) ni del ASAR mismo
    // Opciones: servidor del vendor, TPM, Windows DPAPI
    const expectedHash = fetchExpectedHash(); // API call o TPM read

    if (hash !== expectedHash) {
        dialog.showErrorBox('Integrity Error',
            'Application code has been tampered with.');
        app.quit();
    }
}

// Paso 3: Configuración segura de Electron
new BrowserWindow({
    webPreferences: {
        nodeIntegration: false,       // NUNCA true en producción
        contextIsolation: true,       // SIEMPRE true
        sandbox: true,                // Activar sandbox de Chromium
        enableRemoteModule: false,    // Deprecated, desactivar
    }
});
