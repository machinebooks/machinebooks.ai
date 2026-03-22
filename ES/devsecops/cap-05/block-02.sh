# Extraído de: LibroDevSecOps/cap-05-sca-sbom.md
# Escanear el SBOM generado por Syft
grype sbom:sbom.cdx.json -o json > vulnerabilities.json

# Escanear con umbral de severidad mínima
grype sbom:sbom.cdx.json --fail-on high -o json > vulnerabilities.json

# Escanear directamente un directorio (Grype genera SBOM internamente)
grype dir:. --fail-on critical
