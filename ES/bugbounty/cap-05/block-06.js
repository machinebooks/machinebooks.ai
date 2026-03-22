// Extraído de: LibroBugBounty/cap-05-asar-tampering.md
// Defensas efectivas contra ASAR tampering

// 1. Habilitar fuses de integridad (en el build de Electron)
// En forge.config.js o electron-builder config:
const fuseConfig = {
    // Desactivar RunAsNode
    [FuseV1Options.RunAsNode]: false,
    // Solo cargar desde ASAR (no app/ directorio)
    [FuseV1Options.OnlyLoadAppFromAsar]: true,
    // Verificar integridad del ASAR al cargar
    [FuseV1Options.EnableEmbeddedAsarIntegrityValidation]: true,
    // Cifrar cookies
    [FuseV1Options.EnableCookieEncryption]: true,
    // Desactivar NODE_OPTIONS
    [FuseV1Options.EnableNodeOptionsEnvironmentVariable]: false,
};

// 2. VerificaciÃ³n de firma digital al inicio
// En main.js (primera lÃ­nea):
const { app } = require('electron');
const crypto = require('crypto');
const path = require('path');

function verifyCodeSignature() {
    // Windows: verificar Authenticode
    if (process.platform === 'win32') {
        const { execSync } = require('child_process');
        try {
            const result = execSync(
                `powershell -Command "` +
                `(Get-AuthenticodeSignature '${process.execPath}').Status"`,
                { encoding: 'utf-8' }
            );
            if (!result.trim().includes('Valid')) {
                app.quit();
                return false;
            }
        } catch (e) {
            app.quit();
            return false;
        }
    }
    return true;
}

// 3. Instalar en Program Files (requiere admin)
// En el instalador (NSIS, WiX, etc.):
// InstallDir: $PROGRAMFILES64\MiApp
// NO: $LOCALAPPDATA\MiApp
