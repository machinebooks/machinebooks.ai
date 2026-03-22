// Extraído de: LibroBugBounty/cap-04-electron-superficie.md
// Preload script SEGURO (VS Code pattern):
const { contextBridge, ipcRenderer } = require('electron');

// Solo expone funciones específicas, no APIs genéricas
contextBridge.exposeInMainWorld('api', {
    sendMessage: (channel, data) => {
        // Whitelist de canales permitidos
        const validChannels = ['get-config', 'save-file'];
        if (validChannels.includes(channel)) {
            ipcRenderer.send(channel, data);
        }
    }
});

// Preload script INSEGURO (encontrado en aplicaciones reales):
const { contextBridge } = require('electron');

// Expone require completo — equivale a nodeIntegration: true
contextBridge.exposeInMainWorld('nodeRequire', require);
// O expone child_process directamente
contextBridge.exposeInMainWorld('exec',
    require('child_process').exec);
