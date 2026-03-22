# Extraído de: LibroUsuario/cap-21-la-nube-desde-el-cli.md
# 1. Gasto total del mes en curso
aws ce get-cost-and-usage \
  --time-period Start=2026-03-01,End=2026-03-22 \
  --granularity MONTHLY \
  --metrics "BlendedCost" \
  --output json

# 2. Desglose por servicio
aws ce get-cost-and-usage \
  --time-period Start=2026-03-01,End=2026-03-22 \
  --granularity MONTHLY \
  --metrics "BlendedCost" \
  --group-by Type=DIMENSION,Key=SERVICE \
  --output json

# 3. Mismo período de febrero para comparar
aws ce get-cost-and-usage \
  --time-period Start=2026-02-01,End=2026-02-22 \
  --granularity MONTHLY \
  --metrics "BlendedCost" \
  --group-by Type=DIMENSION,Key=SERVICE \
  --output json
