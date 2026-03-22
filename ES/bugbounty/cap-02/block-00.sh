# Extraído de: LibroBugBounty/cap-02-stack-hunter.md
# 1. El investigador inicia el contenedor
docker-compose up -d

# 2. Claude Code genera un script de anÃ¡lisis
# (Claude escribe el script en /lab/scripts/ via volumen)

# 3. Claude ejecuta el script dentro del contenedor
docker exec aegis-security-lab python3 /lab/scripts/analyze_target.py

# 4. Claude lee los resultados desde /lab/results/ (volumen compartido)
# 5. Claude interpreta y sugiere el siguiente paso
