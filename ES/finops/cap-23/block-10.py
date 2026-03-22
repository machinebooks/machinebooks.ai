# Extraído de: LibroFinOps/cap-23-coste-equipo.md
# Comparación de escenarios: contratación vs consultor
# para cubrir 100 horas de trabajo en los próximos 2 meses

# Escenario A: nueva contratación (Ingeniero IA, €58/hora real)
coste_hora_ingenieros = 58  # €/hora real (incluye SS + overhead)
horas_necesarias = 100
productividad_mes_1 = 0.35
productividad_mes_2 = 0.55
horas_disponibles_2_meses = (160 * productividad_mes_1 + 160 * productividad_mes_2)
# horas_disponibles_2_meses ≈ 144 horas
coste_2_meses_contratacion = 160 * 2 * coste_hora_ingenieros  # Se paga presencia, no productividad
# coste_2_meses_contratacion = €18.560 (precio de la rampa completa)

# Escenario B: consultor externo (mismo perfil, €95/hora)
coste_hora_consultor = 95  # €/hora (sin rampa, productividad inmediata)
coste_100h_consultor = 100 * coste_hora_consultor
# coste_100h_consultor = €9.500

# Conclusión: el consultor es más económico para necesidades puntuales de 2 meses,
# incluso con un precio horario significativamente más alto.
# La nueva contratación es correcta si la necesidad es estructural (>6 meses).
