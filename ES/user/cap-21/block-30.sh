# Extraído de: LibroUsuario/cap-21-la-nube-desde-el-cli.md
# Listar funciones Lambda que empiezan por "api-"
aws lambda list-functions \
  --query 'Functions[?starts_with(FunctionName, `api-`)].FunctionName' \
  --output text | tr '\t' '\n' | while read fn; do
    echo "Actualizando $fn..."
    aws lambda update-function-configuration \
      --function-name "$fn" \
      --environment "Variables={DATABASE_URL=postgresql://prod-db.ejemplo.com:5432/app_db}" \
      --query 'FunctionName' --output text
done
