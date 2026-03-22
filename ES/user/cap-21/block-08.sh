# Extraído de: LibroUsuario/cap-21-la-nube-desde-el-cli.md
# Top funciones Lambda por invocaciones (último mes)
aws lambda list-functions --query 'Functions[].FunctionName' --output text | \
  tr '\t' '\n' | while read fn; do
    invocations=$(aws cloudwatch get-metric-statistics \
      --namespace AWS/Lambda \
      --metric-name Invocations \
      --dimensions Name=FunctionName,Value="$fn" \
      --start-time 2026-03-01T00:00:00Z \
      --end-time 2026-03-22T00:00:00Z \
      --period 1814400 \
      --statistics Sum \
      --query 'Datapoints[0].Sum' --output text 2>/dev/null)
    echo "$invocations $fn"
done | sort -rn | head -10
