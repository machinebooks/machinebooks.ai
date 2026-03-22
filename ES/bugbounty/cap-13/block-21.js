// Extraído de: LibroBugBounty/cap-13-vm-escape-rpc.md
// Pseudocódigo del clasificador Operon (reconstruido del ASAR)
async function classifyArtifact(code) {
    if (!process.env.OPERON_ENABLE_LLM_CLASSIFIER) {
        return { safe: true };  // Desactivado = permitir todo
    }
    try {
        const result = await callClassifierModel(code);
        return result;
    } catch (error) {
        // FAIL OPEN: cualquier error = permitir
        console.warn("Classifier error:", error);
        return { safe: true };
    }
}
