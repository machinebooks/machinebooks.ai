# Extraído de: LibroUsuario/cap-22-contenedores-y-despliegues.md
docker compose exec postgres psql -U app -d staging_db \
  -c "SELECT id, version, status, deployed_at
      FROM deployments
      ORDER BY deployed_at DESC
      LIMIT 10;"
