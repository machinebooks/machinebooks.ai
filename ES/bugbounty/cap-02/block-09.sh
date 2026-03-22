# Extraído de: LibroBugBounty/cap-02-stack-hunter.md
# Claude escribe el script en el volumen compartido
# (esto ocurre automÃ¡ticamente cuando Claude genera cÃ³digo)

# Claude ejecuta el script dentro del contenedor
docker exec aegis-security-lab \
    python3 /lab/scripts/01_pe_analysis.py

# Claude lee el resultado
cat results/pe_analysis.json
