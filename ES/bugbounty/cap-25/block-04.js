// Extraído de: LibroBugBounty/cap-25-caso-wand.md
// Parchear hash en Wand.exe
const exePath = wandRes.replace('resources', 'Wand.exe');
const exeBuf = Buffer.from(fs.readFileSync(exePath));
const oldHashBuf = Buffer.from(oldHash, 'ascii');
const newHashBuf = Buffer.from(newHash, 'ascii');

const idx = exeBuf.indexOf(oldHashBuf);
if (idx !== -1) {
    newHashBuf.copy(exeBuf, idx);
    fs.writeFileSync(exePath, exeBuf);
    console.log(`Hash patched at offset 0x${idx.toString(16)}`);
}
