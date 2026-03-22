# Extraído de: LibroFinOps/cap-23-coste-equipo.md
# Ejemplo de cálculo de impacto de rotación
# Un ingeniero sénior (€62/hora) con 80% dedicación al proyecto deja el equipo

# Periodo sin cobertura: 6 semanas de búsqueda
semanas_busqueda = 6
horas_sem_productivas = 40 * 0.80  # 80% de tiempo productivo
coste_semana = 62 * horas_sem_productivas
coste_busqueda = coste_semana * semanas_busqueda
# coste_busqueda ≈ €11.904 (seis semanas de capacidad perdida en el proyecto)

# Periodo de rampa del sustituto: 4 meses al 60% de productividad efectiva
meses_rampa = 4
factor_productividad_rampa = 0.60
coste_mensual_nuevo = 58 * (40 * 4.33 * 0.80)  # 80% dedicación × horas/mes
# coste_rampa = meses × coste × (1 - factor_productividad) = ineficiencia pagada
coste_ineficiencia_rampa = coste_mensual_nuevo * (1 - factor_productividad_rampa) * meses_rampa
# coste_ineficiencia_rampa ≈ €8.069

# Coste de supervisión del equipo existente: 10% de tiempo del tech lead
coste_supervision = 70 * (40 * 4.33 * 0.10) * meses_rampa
# coste_supervision ≈ €4.851

# Coste total de la rotación (solo impacto en el proyecto)
coste_total_rotacion = coste_busqueda + coste_ineficiencia_rampa + coste_supervision
# coste_total_rotacion ≈ €24.824
# Esto no incluye el coste de RRHH del proceso de selección
