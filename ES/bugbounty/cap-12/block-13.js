// Extraído de: LibroBugBounty/cap-12-prompt-injection-rce.md
// Pseudocódigo reconstruido del handler de run_in_terminal
async function handleRunInTerminal(args) {
    const terminal = vscode.window.createTerminal({
        name: "Copilot",
        hideFromUser: false  // El terminal es visible, pero...
    });
    // Sin validación del comando
    terminal.sendText(args.command);
    // El usuario puede ver el terminal si mira, pero
    // el payload ya se ejecutó antes de que pueda reaccionar
}
