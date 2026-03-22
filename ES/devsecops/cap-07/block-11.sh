# Extraído de: LibroDevSecOps/cap-07-contenedores.md
# Firmar la imagen (keyless, vinculada a la identidad OIDC de GitHub Actions)
cosign sign --yes ghcr.io/org/mi-app:${SHA}

# Verificar la firma (antes de desplegar)
cosign verify \
  --certificate-identity "https://github.com/org/mi-app/.github/workflows/build.yml@refs/heads/main" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  ghcr.io/org/mi-app:${SHA}
