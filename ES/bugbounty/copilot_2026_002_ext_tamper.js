// Extraído de: LibroBugBounty/cap-12-prompt-injection-rce.md
// copilot_2026_002_ext_tamper.js
// Verifica que no hay integridad de código en la extensión

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// Localizar la extensión de Copilot Chat
const extensionDir = path.join(
    process.env.USERPROFILE,
    '.vscode', 'extensions'
);

// Buscar extension.js
const copilotDirs = fs.readdirSync(extensionDir)
    .filter(d => d.startsWith('github.copilot-chat'));

for (const dir of copilotDirs) {
    const extJs = path.join(extensionDir, dir, 'dist', 'extension.js');
    if (fs.existsSync(extJs)) {
        // Calcular hash original
        const original = fs.readFileSync(extJs);
        const hash = crypto.createHash('sha256')
            .update(original).digest('hex');
        console.log(`Original hash: ${hash}`);

        // Modificar (append inofensivo)
        fs.appendFileSync(extJs, '\n// tampered');
        console.log('Modified extension.js — no error from VS Code');

        // VS Code sigue cargando la extensión modificada
        // No hay verificación de firma ni hash
    }
}
