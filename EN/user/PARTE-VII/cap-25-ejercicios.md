# Capítulo 25 — Agentes en equipo: tareas en paralelo con Claude

Ejercicios prácticos para coordinar múltiples instancias de Claude trabajando en paralelo sobre aspectos distintos de un mismo entregable, con una fase final de integración.

---

## Ejercicio 1: Propuesta comercial con 3 agentes en paralelo

**Prerequisitos:** Claude Code instalado. Una carpeta con el briefing del cliente y los datos internos de la empresa (catálogo de servicios, casos de éxito, tarifas).

**Contexto:** Preparar una propuesta comercial implica trabajo técnico, financiero y narrativo. En lugar de hacer todo en serie, lanzamos tres agentes especializados en paralelo y después integramos sus resultados.

### Preparación de la carpeta de trabajo

```
propuesta-equipo/
├── entrada/
│   ├── briefing_cliente.md
│   ├── notas_reunion.md
│   ├── catalogo_servicios.csv
│   ├── tarifas_vigentes.csv
│   └── casos_exito.md
├── agente-tecnico/          ← salida del agente técnico
├── agente-financiero/       ← salida del agente financiero
├── agente-redactor/         ← salida del agente redactor
└── entrega/                 ← propuesta final integrada
```

### Opción A — Un solo comando con tres tareas en paralelo

Usa la capacidad de Claude Code para ejecutar tareas concurrentes desde un único prompt:

```bash
cd /ruta/a/propuesta-equipo

claude -p "$(cat <<'PROMPT'
Necesito preparar una propuesta comercial. Vas a trabajar en tres líneas paralelas
y después integrar los resultados.

TAREA PARALELA 1 — AGENTE TÉCNICO
Lee entrada/briefing_cliente.md y entrada/notas_reunion.md.
Genera agente-tecnico/solucion_tecnica.md con:
- Análisis de requisitos del cliente (funcionales y técnicos).
- Solución técnica propuesta: componentes, arquitectura, integraciones.
- Plan de trabajo: fases, duración estimada, hitos, entregables.
- Riesgos técnicos identificados y mitigaciones.
- Equipo necesario (roles y dedicación estimada).
Extensión: 3-4 páginas. Tono técnico pero comprensible para un director no técnico.

TAREA PARALELA 2 — AGENTE FINANCIERO
Lee entrada/catalogo_servicios.csv y entrada/tarifas_vigentes.csv.
Lee también entrada/briefing_cliente.md para entender el alcance.
Genera agente-financiero/presupuesto.md con:
- Desglose de servicios necesarios con cantidades estimadas.
- Tres escenarios de precio: Básico, Recomendado y Premium.
- Para cada escenario: tabla con servicio, cantidad, precio unitario, subtotal.
- Totales sin IVA, IVA (21%) y total con IVA.
- Condiciones de pago propuestas (50% inicio, 50% entrega, o por hitos).
- Periodo de validez: 30 días.
Extensión: 2-3 páginas. Tablas claras y bien formateadas.

TAREA PARALELA 3 — AGENTE REDACTOR
Lee entrada/briefing_cliente.md, entrada/notas_reunion.md y entrada/casos_exito.md.
Genera agente-redactor/narrativa.md con:
- Resumen ejecutivo (1 página): problema, solución, beneficio clave.
- Sección "Entendimiento de la necesidad" (1 página): demostrar comprensión del contexto.
- Selección de 2 casos de éxito relevantes, adaptados al sector del cliente.
- Sección "Por qué nosotros" (media página): diferenciadores.
- Sección "Próximos pasos" (media página): qué hacer tras aprobar la propuesta.
Tono profesional, orientado al valor. Sin tecnicismos innecesarios.

INTEGRACIÓN FINAL
Cuando las tres tareas estén completas, lee los tres documentos generados y
compón la propuesta final en entrega/propuesta_final.md con esta estructura:

1. Portada (título, fecha, cliente, referencia)
2. Resumen ejecutivo (de agente-redactor)
3. Entendimiento de la necesidad (de agente-redactor)
4. Solución técnica propuesta (de agente-tecnico)
5. Plan de trabajo (de agente-tecnico)
6. Inversión — tres escenarios (de agente-financiero)
7. Casos de éxito (de agente-redactor)
8. Equipo y garantías (de agente-tecnico)
9. Próximos pasos (de agente-redactor)

Verifica que no hay contradicciones entre secciones:
- Lo prometido en la solución técnica debe estar presupuestado.
- Los plazos del plan de trabajo deben ser coherentes con el equipo propuesto.
- El resumen ejecutivo debe reflejar fielmente la solución y el precio.

Si detectas incoherencias, corrígelas en la versión final y documenta los ajustes
al final del documento en una sección "Notas de integración".
PROMPT
)"
```

### Opción B — Tres terminales separadas + terminal de integración

Si prefieres controlar cada agente por separado, abre cuatro terminales:

**Terminal 1 — Agente técnico:**

```bash
cd /ruta/a/propuesta-equipo

claude -p "$(cat <<'PROMPT'
Eres el agente técnico de una propuesta comercial.

Lee los archivos entrada/briefing_cliente.md y entrada/notas_reunion.md.

Genera el archivo agente-tecnico/solucion_tecnica.md con:

1. ANÁLISIS DE REQUISITOS
   - Requisitos funcionales extraídos del briefing y las notas.
   - Requisitos técnicos: infraestructura, integraciones, restricciones.
   - Requisitos no funcionales: rendimiento, disponibilidad, seguridad.

2. SOLUCIÓN TÉCNICA
   - Arquitectura propuesta (componentes y cómo se conectan).
   - Tecnologías recomendadas y por qué.
   - Integraciones con sistemas existentes del cliente.

3. PLAN DE TRABAJO
   - Fases del proyecto con duración estimada.
   - Hitos y entregables por fase.
   - Dependencias entre fases.

4. EQUIPO NECESARIO
   - Roles y dedicación estimada en horas o jornadas.
   - Perfil requerido para cada rol.

5. RIESGOS TÉCNICOS
   - Los 3-5 riesgos más probables.
   - Impacto y probabilidad.
   - Mitigación propuesta.

Tono técnico pero accesible. Extensión: 3-4 páginas.
PROMPT
)"
```

**Terminal 2 — Agente financiero:**

```bash
cd /ruta/a/propuesta-equipo

claude -p "$(cat <<'PROMPT'
Eres el agente financiero de una propuesta comercial.

Lee los archivos:
- entrada/catalogo_servicios.csv (columnas: Servicio, Descripcion, PrecioBase, UnidadMedida)
- entrada/tarifas_vigentes.csv (columnas: Servicio, TarifaHora, TarifaDia, DescuentoVolumen)
- entrada/briefing_cliente.md (para entender el alcance)

Genera el archivo agente-financiero/presupuesto.md con:

1. SERVICIOS SELECCIONADOS
   - Lista de servicios del catálogo que aplican al proyecto.
   - Justificación de por qué se incluye cada uno.

2. ESTIMACIÓN DE CANTIDADES
   - Para cada servicio: cantidad estimada (horas, días, licencias).
   - Base de la estimación (qué requisito cubre).

3. TRES ESCENARIOS DE PRECIO

   ESCENARIO BÁSICO (cubre requisitos mínimos):
   | Servicio | Cantidad | Precio unitario | Subtotal |
   |----------|----------|-----------------|----------|
   | ...      | ...      | ...             | ...      |
   Subtotal: X EUR | IVA (21%): X EUR | TOTAL: X EUR

   ESCENARIO RECOMENDADO (cubre todos los requisitos):
   [misma tabla]

   ESCENARIO PREMIUM (requisitos + valor añadido):
   [misma tabla]

4. COMPARATIVA DE ESCENARIOS
   Tabla resumen con los tres totales y qué incluye/excluye cada uno.

5. CONDICIONES
   - Forma de pago propuesta.
   - Periodo de validez: 30 días desde la fecha de la propuesta.
   - Qué no está incluido en el precio.

Extensión: 2-3 páginas. Tablas claras.
PROMPT
)"
```

**Terminal 3 — Agente redactor:**

```bash
cd /ruta/a/propuesta-equipo

claude -p "$(cat <<'PROMPT'
Eres el agente redactor de una propuesta comercial.

Lee los archivos:
- entrada/briefing_cliente.md
- entrada/notas_reunion.md
- entrada/casos_exito.md

Genera el archivo agente-redactor/narrativa.md con:

1. RESUMEN EJECUTIVO (máximo 1 página)
   - El problema del cliente en 3-4 líneas, usando sus propias palabras del briefing.
   - Nuestra propuesta de solución en 3-4 líneas.
   - El beneficio principal, cuantificado si los datos lo permiten.
   - Una frase de cierre que invite a la acción.

2. ENTENDIMIENTO DE LA NECESIDAD (1 página)
   - Contexto del cliente: sector, situación actual, desafíos.
   - Demostrar que hemos escuchado: referenciar puntos concretos del briefing.
   - Objetivos del proyecto desde la perspectiva del cliente.

3. CASOS DE ÉXITO (1 página)
   - Selecciona los 2 casos de éxito más relevantes para el sector del cliente.
   - Para cada caso: contexto, solución implementada, resultados medibles.
   - Conexión explícita: "Al igual que [cliente del caso], su organización..."

4. POR QUÉ NOSOTROS (media página)
   - 3-4 diferenciadores concretos (no frases genéricas).
   - Experiencia en el sector del cliente.
   - Compromiso de acompañamiento post-proyecto.

5. PRÓXIMOS PASOS (media página)
   - Qué necesitamos del cliente para arrancar.
   - Plazo estimado desde aprobación hasta inicio.
   - Persona de contacto.

Tono: profesional, cercano, orientado al valor. Evitar jerga técnica.
Extensión total: 3-4 páginas.
PROMPT
)"
```

**Terminal 4 — Integración (ejecutar después de que terminen los tres agentes):**

```bash
cd /ruta/a/propuesta-equipo

claude -p "$(cat <<'PROMPT'
Los tres agentes de la propuesta comercial han terminado su trabajo.
Lee los siguientes archivos:
- agente-tecnico/solucion_tecnica.md
- agente-financiero/presupuesto.md
- agente-redactor/narrativa.md

Integra todo en un único documento: entrega/propuesta_final.md

Estructura del documento final:
1. Portada (título, fecha de hoy, nombre del cliente del briefing)
2. Resumen ejecutivo (de narrativa.md)
3. Entendimiento de la necesidad (de narrativa.md)
4. Solución técnica propuesta (de solucion_tecnica.md, secciones 1-2)
5. Plan de trabajo (de solucion_tecnica.md, sección 3)
6. Inversión (de presupuesto.md, los tres escenarios)
7. Casos de éxito (de narrativa.md)
8. Equipo y garantías (de solucion_tecnica.md, sección 4)
9. Próximos pasos (de narrativa.md)

VERIFICACIÓN OBLIGATORIA:
Antes de guardar, comprueba:
1. ¿Los servicios presupuestados coinciden con los descritos en la solución técnica?
2. ¿El equipo propuesto es suficiente para el plan de trabajo planteado?
3. ¿El resumen ejecutivo refleja la solución y los precios reales?
4. ¿Hay contradicciones de plazos entre secciones?
5. ¿El tono es consistente en todo el documento?

Si encuentras incoherencias:
- Corrígelas en la versión integrada.
- Añade al final una sección "Notas de integración" explicando qué ajustaste y por qué.

El documento final debe leerse como si lo hubiera escrito una sola persona.
PROMPT
)"
```

**Qué observar:**
- La Opción A es más cómoda pero depende de que Claude gestione bien la concurrencia interna.
- La Opción B da control total: puedes revisar la salida de cada agente antes de integrar.
- La fase de integración es donde se detectan las incoherencias entre agentes.

---

## Ejercicio 2: Informe con ciclo de escritura y revisión

**Prerequisitos:** Claude Code instalado. Una carpeta con datos para un informe (puede ser cualquier tipo: ventas, proyecto, satisfacción).

**Contexto:** En lugar de generar un informe de una pasada, este ejercicio implementa un ciclo escritor-revisor donde un agente escribe y otro revisa, con correcciones iterativas hasta que el revisor aprueba.

### Preparación

```
informe-ciclo/
├── datos/
│   └── (tus archivos de datos)
├── borradores/
└── entrega/
```

### Paso A — El agente escritor

```bash
cd /ruta/a/informe-ciclo

claude -p "$(cat <<'PROMPT'
Eres el agente ESCRITOR de un informe ejecutivo.

Lee todos los archivos de la carpeta datos/ y genera un informe ejecutivo
completo en borradores/borrador_v1.md.

El informe debe incluir:
1. Resumen ejecutivo (5-8 líneas con los datos más relevantes).
2. Análisis detallado (tablas, comparativas, tendencias).
3. Problemas o alertas detectados.
4. Conclusiones (3-5 puntos).
5. Recomendaciones accionables (3-5 puntos).

Reglas:
- Todos los datos del informe deben provenir de los archivos. No inventes cifras.
- Tono profesional y directo. Si hay datos negativos, exponerlos.
- Incluye las fuentes: de qué archivo sale cada dato.
- Extensión mínima: 3 páginas.
PROMPT
)"
```

### Paso B — El agente revisor

Ejecuta después de que el escritor termine:

```bash
cd /ruta/a/informe-ciclo

claude -p "$(cat <<'PROMPT'
Eres el agente REVISOR de un informe ejecutivo.

Lee el borrador en borradores/borrador_v1.md y los datos originales en datos/.

Revisa el informe con este checklist:

PRECISIÓN DE DATOS
- ¿Las cifras del informe coinciden con los datos de los archivos originales?
- ¿Los porcentajes y variaciones están bien calculados?
- ¿Se atribuye correctamente cada dato a su fuente?

COMPLETITUD
- ¿Se han analizado todos los archivos de datos/ o se ha omitido alguno?
- ¿Faltan análisis relevantes que los datos permiten hacer?
- ¿Las conclusiones están respaldadas por los datos presentados?

CALIDAD NARRATIVA
- ¿El resumen ejecutivo captura lo esencial?
- ¿El tono es profesional y directo?
- ¿Hay frases vagas o de relleno que no aportan?
- ¿Las recomendaciones son concretas y accionables?

FORMATO
- ¿Las tablas están bien formateadas?
- ¿La estructura es lógica y fácil de seguir?
- ¿Ortografía y gramática correctas?

Genera borradores/revision_v1.md con:
- VEREDICTO: APROBADO o REQUIERE CORRECCIONES
- Lista numerada de observaciones, cada una con:
  - Sección afectada
  - Problema detectado
  - Corrección sugerida
  - Severidad: CRÍTICA (dato incorrecto), IMPORTANTE (falta contenido), MENOR (estilo)

Si el veredicto es APROBADO, copia el borrador a entrega/informe_final.md.
PROMPT
)"
```

### Paso C — El agente escritor corrige (si es necesario)

Si el revisor encontró correcciones:

```bash
cd /ruta/a/informe-ciclo

claude -p "$(cat <<'PROMPT'
Eres el agente ESCRITOR. El revisor ha evaluado tu borrador.

Lee:
- borradores/borrador_v1.md (tu borrador original)
- borradores/revision_v1.md (las observaciones del revisor)
- Los datos originales en datos/

Aplica TODAS las correcciones señaladas por el revisor:
- Las CRÍTICAS deben corregirse verificando contra los datos originales.
- Las IMPORTANTES deben añadir el contenido faltante.
- Las MENORES deben corregirse si no alteran el sentido.

Genera borradores/borrador_v2.md con todas las correcciones aplicadas.
Al final del documento, añade una sección "Cambios aplicados en v2" listando
qué corregiste en respuesta a cada observación.
PROMPT
)"
```

Después, vuelve a ejecutar el agente revisor sobre `borrador_v2.md` (cambiando las versiones en el prompt). Repite el ciclo hasta que el veredicto sea APROBADO.

**Qué observar:**
- El ciclo escritor-revisor produce informes de mayor calidad que una sola pasada.
- El revisor verifica los datos contra las fuentes originales, no solo la redacción.
- Cada iteración deja trazabilidad completa: borradores, revisiones y cambios aplicados.

---

## Ejercicio 3: Preparación de reunión con 3 agentes en paralelo

**Prerequisitos:** Claude Code instalado. Datos de seguimiento de un proyecto, registro de incidencias y calendario de la reunión.

**Contexto:** Preparar una reunión de seguimiento semanal requiere consolidar el estado del proyecto, analizar las incidencias de la semana y preparar el orden del día. Tres agentes trabajan en paralelo sobre estos tres frentes y un cuarto integra el dosier completo.

### Preparación

```
reunion-semanal/
├── datos/
│   ├── tareas_proyecto.csv         ← columnas: ID, Tarea, Responsable, Estado, FechaLimite, Prioridad
│   ├── incidencias_semana.csv      ← columnas: ID, Fecha, Tipo, Descripcion, Impacto, Estado, Responsable
│   ├── acta_reunion_anterior.md    ← acta de la reunión pasada con compromisos
│   └── calendario_hitos.csv        ← columnas: Hito, FechaPrevista, FechaReal, Estado
├── agentes/
└── entrega/
```

### Opción A — Un solo comando con tres tareas en paralelo

```bash
cd /ruta/a/reunion-semanal

claude -p "$(cat <<'PROMPT'
Prepara el dosier para la reunión de seguimiento semanal del proyecto.
Trabaja en tres líneas paralelas y después integra los resultados.

TAREA PARALELA 1 — ESTADO DEL PROYECTO
Lee datos/tareas_proyecto.csv, datos/calendario_hitos.csv y datos/acta_reunion_anterior.md.
Genera agentes/estado_proyecto.md con:

1. RESUMEN DE ESTADO
   - Semáforo general: Verde/Amarillo/Rojo (basado en los datos, no en opinión).
   - Criterio: Verde si >80% tareas en plazo, Amarillo si 60-80%, Rojo si <60%.

2. PROGRESO DE TAREAS
   - Tabla: tareas completadas esta semana, en curso, retrasadas.
   - Por cada tarea retrasada: responsable, días de retraso, impacto.

3. HITOS
   - Próximos hitos en los siguientes 14 días.
   - Hitos retrasados con nueva fecha estimada.

4. COMPROMISOS DE LA REUNIÓN ANTERIOR
   - Lee el acta anterior y verifica qué compromisos se cumplieron.
   - Lista: compromiso, responsable, estado (cumplido/pendiente/parcial).

TAREA PARALELA 2 — ANÁLISIS DE INCIDENCIAS
Lee datos/incidencias_semana.csv.
Genera agentes/analisis_incidencias.md con:

1. RESUMEN DE INCIDENCIAS
   - Total de la semana, abiertas vs cerradas.
   - Distribución por tipo e impacto.

2. INCIDENCIAS CRÍTICAS
   - Detalle de cada incidencia con impacto alto o crítico.
   - Estado actual y acciones pendientes.

3. TENDENCIAS
   - ¿Hay más o menos incidencias que la semana anterior?
   - ¿Hay un tipo que se repite? ¿Indica un problema sistémico?

4. ACCIONES RECOMENDADAS
   - Para cada incidencia abierta: propuesta de resolución y responsable sugerido.

TAREA PARALELA 3 — ORDEN DEL DÍA
Lee datos/acta_reunion_anterior.md para contexto.
Lee los otros archivos de datos/ para identificar temas urgentes.
Genera agentes/orden_del_dia.md con:

1. ORDEN DEL DÍA PROPUESTO
   - Punto 1: Revisión de estado general (5 min)
   - Punto 2: Tareas retrasadas — plan de recuperación (10 min)
   - Punto 3: Incidencias críticas abiertas (10 min)
   - Punto 4: Compromisos pendientes de la reunión anterior (5 min)
   - Punto 5: Próximos hitos y riesgos (5 min)
   - Punto 6: Decisiones necesarias (10 min)
   - Punto 7: Nuevos compromisos y cierre (5 min)

2. PREGUNTAS PREPARADAS
   - Para cada punto del orden del día, 2-3 preguntas concretas
     que el moderador debería plantear.

3. DECISIONES PENDIENTES
   - Lista de decisiones que necesitan tomarse en esta reunión,
     basadas en los datos analizados.

INTEGRACIÓN FINAL
Lee los tres documentos generados y compón el dosier completo
en entrega/dosier_reunion_YYYY-MM-DD.md con:

1. PORTADA (proyecto, fecha, participantes si se conocen)
2. ORDEN DEL DÍA (de agentes/orden_del_dia.md)
3. ESTADO DEL PROYECTO (de agentes/estado_proyecto.md)
4. ANÁLISIS DE INCIDENCIAS (de agentes/analisis_incidencias.md)
5. PUNTOS DE DECISIÓN (consolidado de las tres fuentes)
6. PLANTILLA DE ACTA (secciones vacías para rellenar durante la reunión:
   decisiones tomadas, compromisos nuevos con responsable y fecha)

El dosier debe poder imprimirse y usarse directamente en la reunión.
PROMPT
)"
```

### Opción B — Tres terminales separadas + terminal de integración

**Terminal 1 — Agente de estado del proyecto:**

```bash
cd /ruta/a/reunion-semanal

claude -p "$(cat <<'PROMPT'
Eres el agente encargado del ESTADO DEL PROYECTO para la reunión semanal.

Lee:
- datos/tareas_proyecto.csv
- datos/calendario_hitos.csv
- datos/acta_reunion_anterior.md

Genera agentes/estado_proyecto.md con:

1. SEMÁFORO GENERAL
   Calcula el porcentaje de tareas en plazo:
   - Verde: >80% en plazo
   - Amarillo: 60-80% en plazo
   - Rojo: <60% en plazo

2. TABLA DE PROGRESO
   | Tarea | Responsable | Estado | Fecha límite | Días retraso |
   Solo incluye tareas activas o retrasadas (no las completadas hace más de 7 días).

3. HITOS PRÓXIMOS (siguientes 14 días)
   | Hito | Fecha prevista | Estado | Riesgo de retraso |

4. COMPROMISOS DE LA REUNIÓN ANTERIOR
   Lee el acta anterior y para cada compromiso indica:
   | Compromiso | Responsable | Estado (cumplido/pendiente/parcial) |

5. ALERTAS
   - Tareas con más de 5 días de retraso.
   - Hitos en riesgo.
   - Compromisos incumplidos.
PROMPT
)"
```

**Terminal 2 — Agente de incidencias:**

```bash
cd /ruta/a/reunion-semanal

claude -p "$(cat <<'PROMPT'
Eres el agente encargado del ANÁLISIS DE INCIDENCIAS para la reunión semanal.

Lee datos/incidencias_semana.csv.

Genera agentes/analisis_incidencias.md con:

1. RESUMEN
   - Total incidencias de la semana.
   - Abiertas: X | Cerradas: X | En curso: X
   - Distribución por tipo (tabla).
   - Distribución por impacto: Crítico, Alto, Medio, Bajo.

2. INCIDENCIAS CRÍTICAS (detalle completo)
   Para cada incidencia con impacto Crítico o Alto:
   - ID, fecha, descripción completa.
   - Estado actual y responsable.
   - Acciones tomadas hasta ahora.
   - Acción pendiente para resolución.

3. PATRONES
   - ¿Hay tipos de incidencia recurrentes?
   - ¿Algún componente o área concentra las incidencias?
   - Comparativa implícita: ¿la situación mejora o empeora?

4. PROPUESTAS DE ACCIÓN
   Para cada incidencia abierta, propón:
   - Acción concreta para resolverla.
   - Responsable sugerido.
   - Plazo razonable.
PROMPT
)"
```

**Terminal 3 — Agente de orden del día:**

```bash
cd /ruta/a/reunion-semanal

claude -p "$(cat <<'PROMPT'
Eres el agente encargado del ORDEN DEL DÍA para la reunión semanal.

Lee todos los archivos de datos/ para identificar los temas más relevantes.

Genera agentes/orden_del_dia.md con:

1. ORDEN DEL DÍA (con tiempos asignados, total 50 minutos)
   Para cada punto:
   - Título del punto.
   - Tiempo asignado.
   - Objetivo: qué debe salir de este punto (información, decisión, compromiso).
   - Responsable de presentar el punto.

2. PREGUNTAS PREPARADAS PARA EL MODERADOR
   Para cada punto del orden del día, 2-3 preguntas que obliguen a ir al grano:
   - "¿Cuál es la causa raíz del retraso en [tarea X]?"
   - "¿Qué necesitas para desbloquear [incidencia Y] esta semana?"
   - "¿Podemos comprometernos con la fecha [Z] para el hito?"

3. DECISIONES QUE DEBEN TOMARSE
   Lista de decisiones que no pueden posponerse:
   - Descripción de la decisión.
   - Opciones sobre la mesa.
   - Información necesaria para decidir (y si está disponible).

4. PLANTILLA DE ACTA
   Secciones vacías listas para rellenar durante la reunión:
   - Asistentes: ___
   - Decisiones tomadas: ___
   - Compromisos nuevos: | Compromiso | Responsable | Fecha | ___
   - Fecha próxima reunión: ___
PROMPT
)"
```

**Terminal 4 — Integración (ejecutar después de que terminen los tres agentes):**

```bash
cd /ruta/a/reunion-semanal

claude -p "$(cat <<'PROMPT'
Los tres agentes de preparación de reunión han terminado.

Lee:
- agentes/estado_proyecto.md
- agentes/analisis_incidencias.md
- agentes/orden_del_dia.md

Integra todo en entrega/dosier_reunion.md con esta estructura:

1. PORTADA
   - Proyecto: [extraer del contexto]
   - Fecha: la de hoy
   - Tipo: Reunión de seguimiento semanal

2. ORDEN DEL DÍA (de orden_del_dia.md)

3. ESTADO DEL PROYECTO (de estado_proyecto.md)
   - Incluye el semáforo general en la primera línea.

4. INCIDENCIAS DE LA SEMANA (de analisis_incidencias.md)

5. PUNTOS DE DECISIÓN
   Consolida las decisiones pendientes identificadas por los tres agentes.
   Elimina duplicados. Ordena por urgencia.

6. PREGUNTAS PARA EL MODERADOR
   Consolida las preguntas de los tres agentes, organizadas por punto del orden del día.

7. PLANTILLA DE ACTA
   Secciones vacías para rellenar en la reunión.

VERIFICACIÓN:
- ¿El orden del día cubre todos los problemas detectados por los otros agentes?
- ¿Las preguntas del moderador abordan las alertas y los retrasos?
- ¿Hay decisiones pendientes que no tienen punto en el orden del día?

Si falta algo, ajusta el orden del día para incluirlo.
El dosier debe poder imprimirse y servir como guía completa para la reunión.
PROMPT
)"
```

**Qué observar:**
- Cada agente tiene un enfoque especializado: datos del proyecto, incidencias y facilitación de la reunión.
- La integración no es un simple corta-pega: verifica coherencia y añade lo que falte.
- La plantilla de acta convierte el dosier en un documento que se usa durante y después de la reunión.

---

## Preguntas de reflexión

Después de completar los ejercicios, considera:

1. **Paralelismo real vs secuencial:** ¿Notaste diferencia de tiempo entre la Opción A y la Opción B? ¿Cuándo compensa usar una u otra?
2. **Calidad de la integración:** ¿El documento integrado se lee como si lo hubiera escrito una sola persona, o se notan las costuras entre agentes?
3. **Coordinación sin contexto compartido:** Cada agente trabaja de forma independiente. ¿Qué información compartirías entre agentes para mejorar la coherencia sin perder el paralelismo?
