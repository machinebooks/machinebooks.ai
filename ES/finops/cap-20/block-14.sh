# Extraído de: LibroFinOps/cap-20-policy-as-code.md
# Rollback de una política FinOps en producción
# 1. Identificar el commit del cambio problemático
git log --oneline policies/task-types/compliance_report.yaml
# abc1234 Reducir límite output tokens compliance a 4000 (2025-03-15)
# def5678 Actualizar compliance_report para incluir análisis NIS2

# 2. Revertir al estado anterior
git revert abc1234 --no-edit
# Genera: "Revert 'Reducir límite output tokens compliance a 4000'"

# 3. Push a main → despliegue automático via CI/CD
git push origin main
# El pipeline valida, despliega a staging, verifica, promueve
