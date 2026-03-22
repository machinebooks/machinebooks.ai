# Extraído de: LibroDevSecOps/cap-05-sca-sbom.md
# Generar SBOM del directorio del proyecto
syft dir:. -o cyclonedx-json > sbom.cdx.json

# Generar SBOM de una imagen Docker
syft registry:mi-org/mi-app:latest -o cyclonedx-json > sbom.cdx.json

# Generar SBOM con información de licencias detallada
syft dir:. -o cyclonedx-json --file sbom.cdx.json \
  --catalogers all
