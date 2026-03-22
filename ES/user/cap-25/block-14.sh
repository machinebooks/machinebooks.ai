# Extraído de: LibroUsuario/cap-25-agentes-en-equipo.md
cd /home/usuario/propuesta-cliente

claude -p "
Necesito preparar una propuesta comercial para Tech Solutions.
Lee glosario.md para las convenciones y datos/cliente-tech-solutions.md
para el contexto.

Divide el trabajo en tres tareas paralelas:

TAREA PARALELA 1 — Análisis del cliente:
- Lee datos/cliente-tech-solutions.md y datos/proyectos-anteriores.csv
- Genera un análisis en partes/analisis-cliente.md que incluya:
  * Perfil de la empresa (sector, tamaño, facturación)
  * Historial de relación con nosotros (proyectos, satisfacción, pagos)
  * Análisis de la necesidad actual (qué piden, por qué, urgencia)
  * Oportunidades: qué servicios adicionales podríamos ofrecerles
  * Riesgos: qué podría salir mal y cómo mitigarlo
- Extensión: 800-1.200 palabras

TAREA PARALELA 2 — Estimación económica:
- Lee datos/tarifas-2025.csv y datos/servicios-catalogo.csv
- Lee la necesidad del cliente en datos/cliente-tech-solutions.md
- Genera un presupuesto detallado en partes/estimacion-economica.md:
  * Desglose del proyecto en fases (consultoría, desarrollo, implantación, formación)
  * Para cada fase: duración, perfiles necesarios, dedicación, coste unitario y total
  * Tabla resumen con subtotales por fase
  * Descuento del 10% por cliente existente
  * Total sin IVA, IVA (21%) y total con IVA
  * Condiciones de pago: 30% inicio, 40% hito intermedio, 30% entrega
  * Todos los importes en formato del glosario

TAREA PARALELA 3 — Narrativa comercial:
- Lee datos/cliente-tech-solutions.md para el contexto
- Genera la narrativa en partes/narrativa-propuesta.md con estas secciones:
  * Resumen ejecutivo (1 párrafo convincente)
  * Comprensión de la necesidad (reformular lo que el cliente pide)
  * Solución propuesta (descripción en lenguaje no técnico)
  * Plan de trabajo (cronograma de 4 meses con hitos)
  * Equipo (perfiles que participarán, sin nombres)
  * Garantías y soporte post-implantación
  * Por qué elegirnos (basado en historial de satisfacción)
  * Próximos pasos (reunión de presentación, validez 30 días)
  * Dejar marcadores [INSERTAR_ANALISIS] y [INSERTAR_PRESUPUESTO]
    donde corresponda

Cuando las tres tareas terminen, integra los resultados:
1. Lee los tres archivos de partes/
2. Integra el análisis y el presupuesto en la narrativa,
   reemplazando los marcadores
3. Verifica coherencia: cifras, fechas, nombres, formato
4. Genera resultado/propuesta-final.md
"
