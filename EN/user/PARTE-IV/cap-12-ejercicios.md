# Capítulo 12 — Calendario y tareas: planificación, priorización y protección del tiempo

Ejercicios prácticos con prompts listos para copiar y pegar en Claude Code o Claude Desktop. Estos ejercicios asumen que tienes acceso a tu calendario (Google Calendar u Outlook vía MCP) y un archivo de tareas en formato texto, Markdown o cualquier formato que el agente pueda leer.

---

## Ejercicio 1: Verificar la conexión con el calendario

**Prerequisitos:** Tener configurado el servidor MCP de Google Calendar u Outlook en Claude Desktop o Claude Code.

**Contexto:** Igual que con el email, el primer paso es confirmar que el agente ve tu calendario correctamente. Este prompt verifica la conexión y te muestra un resumen para que compruebes que los datos coinciden con lo que ves en tu aplicación de calendario.

```text
Verifica que tienes acceso a mi calendario.
Muéstrame:
1. La cuenta conectada y los calendarios disponibles
   (principal, compartidos, suscripciones).
2. Todos los eventos de esta semana (lunes a viernes), con:
   - Hora de inicio y fin
   - Título del evento
   - Si tiene videollamada (Zoom, Meet, Teams)
   - Asistentes (si los hay)
3. Horas totales ocupadas en reuniones esta semana.
4. Bloques libres de más de 1 hora disponibles.

Si algo falla en la conexión, explícame qué está fallando
y cómo solucionarlo paso a paso.
```

---

## Ejercicio 2: Planificación completa de la semana

**Prerequisitos:** Acceso al calendario, bandeja de entrada reciente y un archivo de tareas pendientes (puede ser un .md, .txt o lista en cualquier formato).

**Contexto:** La planificación semanal es el ejercicio más valioso de productividad personal. Este prompt cruza tres fuentes de información (calendario, email y tareas) para generar un plan realista, no una lista de deseos imposible.

```text
Necesito planificar mi semana completa. Tienes acceso a tres fuentes:

1. MI CALENDARIO: los eventos ya confirmados de esta semana.
2. MI BANDEJA DE ENTRADA: los emails recientes con compromisos o peticiones.
3. MI ARCHIVO DE TAREAS: [pega aquí tu lista de tareas o indica la ruta
   del archivo].

Con estas tres fuentes, genera un plan semanal que incluya:

### ANÁLISIS PREVIO
- Horas ya comprometidas en reuniones (del calendario).
- Horas disponibles reales para trabajo individual.
- Tareas pendientes que tienen plazo esta semana.
- Compromisos adquiridos por email que requieren tiempo.

### PLAN DÍA A DÍA (lunes a viernes)
Para cada día:
- Bloques de tiempo asignados a cada tarea (con hora de inicio y fin).
- Reuniones existentes del calendario.
- Buffer de 30 minutos antes de reuniones importantes
  para preparación.
- Bloque de 30 minutos para procesar email (mañana y tarde).
- Al menos 1 bloque de 2+ horas de trabajo concentrado al día.

### ALERTAS
- Tareas que NO caben en la semana con el calendario actual.
- Días sobrecargados (>7 horas de compromisos).
- Reuniones que podrían ser un email (si detectas alguna).

### DECISIONES QUE NECESITAS DE MÍ
- Qué tareas priorizar si no cabe todo.
- Qué reuniones podrían moverse o cancelarse.

Formato: tabla por día con columnas [Hora | Actividad | Tipo | Duración].
```

---

## Ejercicio 3: Gestión de conflictos de calendario

**Prerequisitos:** Acceso al calendario. Funciona mejor cuando hay semanas cargadas con solapamientos o días sin hueco.

**Contexto:** Los conflictos de calendario no son solo solapamientos de hora. También son días sin descanso, reuniones consecutivas sin transición, o semanas donde no queda tiempo para hacer el trabajo real. Este prompt detecta todos esos problemas.

```text
Revisa mi calendario de la próxima semana y busca estos tipos
de conflictos:

1. SOLAPAMIENTOS: eventos que coinciden en horario.
   Para cada uno, dime cuál es más importante y sugiere
   una acción (declinar, mover, pedir grabación).

2. REUNIONES CONSECUTIVAS: bloques de 3+ reuniones sin descanso.
   Sugiere dónde insertar 15 minutos de transición.

3. DÍAS SIN TRABAJO PROFUNDO: días donde no hay ni un bloque
   de 90+ minutos libres. Sugiere qué reunión mover para abrir hueco.

4. REUNIONES SIN AGENDA: eventos que no tienen descripción
   ni documentos adjuntos. Genera un email para pedir agenda
   al organizador.

5. REUNIONES FANTASMA: eventos recurrentes que llevan semanas
   sin asistentes confirmados o que siempre se cancelan.
   Sugiere cuáles eliminar.

Para cada conflicto, genera la acción concreta:
- Si es declinar: borrador del email de declinación.
- Si es mover: propuesta de nuevo horario.
- Si es cancelar: borrador de notificación.

Muéstrame un "antes y después" del calendario con los cambios propuestos.
```

---

## Ejercicio 4: Archivo de tareas como fuente de verdad

**Prerequisitos:** Un archivo de tareas en formato Markdown o texto plano. Si no tienes uno, este prompt te ayuda a crearlo.

**Contexto:** Las tareas viven dispersas: en emails, en notas de reuniones, en mensajes de chat, en tu cabeza. Este prompt centraliza todo en un único archivo que se convierte en tu fuente de verdad.

```text
Voy a usar un archivo Markdown como mi sistema de gestión de tareas.
La ruta será: ~/tareas/tareas-semana.md

Analiza estas fuentes para extraer TODAS mis tareas pendientes:
1. Los emails de esta semana donde se me pide algo o me comprometo
   a algo.
2. Mi calendario de esta semana (las reuniones generan acciones
   previas y posteriores).
3. [Si tienes un archivo de tareas existente, indícalo aquí].

Crea el archivo con esta estructura:

# Tareas — Semana del [fecha]

## 🔴 Urgente (hacer hoy)
- [ ] Tarea — Origen: [email/reunión/manual] — Plazo: [fecha]

## 🟡 Esta semana
- [ ] Tarea — Origen: [email/reunión/manual] — Plazo: [fecha]

## 🟢 Próxima semana o sin plazo
- [ ] Tarea — Origen: [email/reunión/manual]

## ✅ Completadas esta semana
- [x] Tarea — Completada: [fecha]

## Notas
- [Contexto adicional, dependencias, enlaces relevantes]

Reglas:
- Cada tarea debe ser una acción concreta (no "revisar el proyecto"
  sino "revisar y comentar el documento X del proyecto Y").
- Si una tarea depende de otra persona, indicarlo.
- Si una tarea tiene entregable, especificar qué exactamente.
```

---

## Ejercicio 5: Reglas de priorización personalizadas

**Prerequisitos:** Tu archivo de tareas del Ejercicio 4 o cualquier lista de tareas pendientes.

**Contexto:** No basta con listar tareas; necesitas un sistema de priorización que refleje TUS criterios reales, no una matriz genérica. Este prompt te ayuda a definir tus reglas y luego las aplica automáticamente.

```text
Quiero definir mis reglas de priorización de tareas. Primero, ayúdame
a establecer los criterios. Mis reglas actuales (ajústalas si ves
incoherencias):

1. Si tiene plazo hoy o mañana → prioridad máxima, sin excepciones.
2. Si bloquea a otra persona de mi equipo → prioridad alta.
3. Si es visible para un cliente o un superior → prioridad alta.
4. Si no tiene plazo y solo me afecta a mí → prioridad baja
   (aunque sea importante).
5. Si lleva más de 5 días en la lista sin avanzar → revisar si
   realmente debo hacerla yo o delegarla.
6. Si requiere más de 4 horas de trabajo concentrado → partir
   en subtareas.

Ahora aplica estas reglas a mi lista de tareas actual:
[pega aquí tu lista de tareas o indica la ruta del archivo]

Para cada tarea:
- Asigna prioridad (1-5) según mis reglas.
- Explica en una línea por qué tiene esa prioridad.
- Si una tarea debería delegarse, dime a quién y por qué.
- Si una tarea debería eliminarse, argumenta por qué.

Al final, muéstrame la lista reordenada de arriba (hacer primero)
a abajo (puede esperar).
```

---

## Ejercicio 6: Replanificación tras un cambio inesperado

**Prerequisitos:** Un plan semanal ya establecido (del Ejercicio 2) y un evento inesperado que cambia las prioridades.

**Contexto:** Ningún plan sobrevive al lunes intacto. Este prompt simula la llegada de un imprevisto y te ayuda a replanificar sin entrar en pánico, moviendo fichas de forma racional.

```text
Mi plan de la semana acaba de romperse. Ha ocurrido lo siguiente:

[Describe el cambio. Ejemplo:]
Mi jefe me acaba de asignar una presentación urgente para el director
general que debe estar lista el miércoles a las 10:00.
Estimación: necesito al menos 6 horas de trabajo concentrado para
prepararla (investigar datos, crear slides, ensayar).

Mi plan actual de la semana es:
[pega tu plan semanal o indica la ruta del archivo]

Necesito que hagas lo siguiente:

1. IMPACTO: ¿qué tareas de mi plan actual no puedo completar
   si dedico 6 horas a la presentación?

2. OPCIONES DE REPLANIFICACIÓN: dame 2 escenarios distintos.
   - Escenario A: mínimo impacto en plazos existentes.
   - Escenario B: mínimo impacto en calidad de entregables.

3. COMUNICACIÓN: para cada tarea que se retrase, genera un email
   breve al interesado avisando del nuevo plazo.

4. PLAN ACTUALIZADO: el plan día a día revisado con la presentación
   incluida y las tareas reorganizadas.

5. PLAN DE CONTINGENCIA: si la presentación se complica y necesito
   más de 6 horas, ¿qué más puedo sacrificar?

No intentes meterlo todo. Prefiero un plan realista donde algunas
cosas se retrasen a un plan imposible donde no llego a nada.
```

---

## Ejercicio 7: Preparar reuniones desde el calendario

**Prerequisitos:** Acceso al calendario con los eventos del día siguiente.

**Contexto:** La preparación de reuniones es tiempo que casi nadie invierte, pero que marca la diferencia entre una reunión productiva y una reunión perdida. Este prompt revisa tus reuniones de mañana y te prepara para cada una.

```text
Revisa las reuniones de mañana en mi calendario.
Para cada reunión, genera una ficha de preparación:

### [Título de la reunión] — [Hora]

**Asistentes:** [lista]
**Duración:** [X minutos]
**Tipo:** [decisión / seguimiento / informativa / brainstorming]

**Contexto:**
- ¿Qué emails recientes he intercambiado con estos asistentes?
- ¿Hay tareas abiertas relacionadas con esta reunión en mi archivo?
- ¿Qué se decidió en la última reunión con estas personas (si encuentras
  información)?

**Mi preparación:**
- 3 puntos que debería llevar preparados.
- 1 pregunta clave que debería hacer.
- Documentos o datos que debería tener abiertos.

**Objetivo de salida:**
- ¿Qué resultado concreto necesito de esta reunión?
- ¿Qué decisión espero que se tome?

**Tiempo de preparación estimado:** [X minutos]

Al final, dame el orden en que debería prepararlas,
empezando por la que requiere más preparación.
```

---

## Ejercicio 8: Detectar semanas sobrecargadas

**Prerequisitos:** Acceso al calendario de las próximas 2-4 semanas.

**Contexto:** La sobrecarga no se ve cuando miras día a día. Se ve cuando miras la tendencia de varias semanas. Este prompt analiza tu calendario con perspectiva y te alerta antes de que llegue la crisis.

```text
Analiza mi calendario de las próximas 4 semanas.
Genera un informe de carga con esta estructura:

## MAPA DE CALOR SEMANAL
Para cada semana, muéstrame:
- Horas totales en reuniones.
- Horas disponibles para trabajo individual.
- Número de reuniones por día.
- Día más cargado y día más libre.

Usa un formato visual (barras ASCII o similar):
Semana 1: ████████░░ (32h reuniones / 8h libres)
Semana 2: ██████████ (40h reuniones / 0h libres) ⚠️

## ALERTAS ROJAS
- Semanas donde las reuniones superan el 70% del horario laboral.
- Días con más de 6 horas de reuniones consecutivas.
- Semanas donde no hay ni un solo bloque de 3+ horas libres.

## ANÁLISIS DE REUNIONES
- ¿Cuántas reuniones son recurrentes vs. puntuales?
- ¿Cuántas tienen más de 6 asistentes? (candidatas a "¿debería estar yo?")
- ¿Cuántas no tienen agenda definida?

## RECOMENDACIONES
- Reuniones que podría declinar o delegar (con justificación).
- Días donde debería bloquear tiempo antes de que lo ocupen.
- Reuniones recurrentes que deberían reducir frecuencia
  (semanal → quincenal).

Sé concreto: no me digas "deberías tener menos reuniones".
Dime cuáles sobran y por qué.
```

---

## Ejercicio 9: Revisión de fin de día

**Prerequisitos:** Acceso al calendario del día actual y al archivo de tareas.

**Contexto:** Cinco minutos al final del día para cerrar mentalmente la jornada. Este prompt compara lo que planificaste con lo que realmente ocurrió y prepara el arranque del día siguiente.

```text
Son las 18:00 y estoy cerrando el día. Revisa lo siguiente:

1. CALENDARIO DE HOY: ¿qué reuniones tuve?
2. MI ARCHIVO DE TAREAS: ¿qué tareas estaban marcadas para hoy?

Genera mi revisión de fin de día:

## LO QUE COMPLETÉ
- Tareas terminadas hoy (marca como ✅ en el archivo de tareas).
- Reuniones que asistí y sus resultados principales.

## LO QUE NO COMPLETÉ
- Tareas que quedaron pendientes. Para cada una:
  - ¿Por qué no se completó? (falta de tiempo / bloqueo / prioridad cambiada)
  - ¿Cuándo la reubico? Propón un día concreto.

## NUEVAS TAREAS QUE SURGIERON HOY
- Compromisos adquiridos en reuniones.
- Peticiones recibidas por email hoy.
- Añádelas al archivo de tareas en la sección correcta.

## MAÑANA
- Las 3 primeras tareas de mañana, en orden.
- Reuniones de mañana con preparación necesaria (sí/no).
- ¿Hay algo que debería hacer esta noche (revisar un documento,
  enviar un email)?

Actualiza mi archivo de tareas con todos estos cambios.
```

---

## Ejercicio 10: Revisión semanal del viernes

**Prerequisitos:** Acceso al calendario de la semana, archivo de tareas y bandeja de entrada.

**Contexto:** La revisión semanal es el ritual más importante de cualquier sistema de productividad. Este prompt automatiza la parte mecánica (recopilar datos) para que tú puedas centrarte en la parte estratégica (decidir qué importa la próxima semana).

```text
Es viernes por la tarde. Ejecuta mi revisión semanal completa.

## PARTE 1: RETROSPECTIVA
Analiza mi calendario, emails y archivo de tareas de esta semana.

- Tareas completadas: lista con fecha de cierre.
- Tareas no completadas: lista con razón probable.
- Reuniones: total de horas, reuniones más productivas
  y menos productivas (basándote en si generaron acciones claras).
- Emails: pendientes de respuesta que llevo más de 48h sin contestar.
- Compromisos incumplidos: cosas que prometí y no hice.

## PARTE 2: PRÓXIMA SEMANA
Analiza mi calendario de la próxima semana.

- Reuniones confirmadas: tabla con día, hora, título, preparación
  necesaria.
- Horas disponibles por día para trabajo individual.
- Tareas que arrastro de esta semana + nuevas tareas identificadas.
- Propuesta de plan semanal (asignar tareas a bloques libres).

## PARTE 3: DECISIONES PENDIENTES
- Lista de decisiones que estoy posponiendo (basándote en tareas
  que llevan más de 1 semana sin avanzar).
- Para cada una: qué información me falta para decidir.

## PARTE 4: ACTUALIZACIÓN DEL ARCHIVO DE TAREAS
- Mueve las tareas completadas a la sección "Completadas".
- Reordena las pendientes según prioridad para la próxima semana.
- Elimina o archiva tareas que llevan más de 3 semanas sin moverse.
- Añade las tareas nuevas que surgieron esta semana.

Guarda el archivo de tareas actualizado.
```

---

## Ejercicio 11: Proteger el tiempo de trabajo concentrado

**Prerequisitos:** Acceso al calendario de la próxima semana.

**Contexto:** El trabajo que realmente importa (pensar, escribir, programar, diseñar) necesita bloques largos sin interrupciones. Este prompt analiza tu semana y bloquea tiempo para trabajo profundo antes de que las reuniones se lo coman.

```text
Revisa mi calendario de la próxima semana y ayúdame a proteger
tiempo de trabajo concentrado.

Mis reglas:
- Necesito mínimo 2 bloques de 2+ horas de trabajo concentrado al día.
- Mis horas más productivas son de 9:00 a 12:00 (proteger esta franja).
- No quiero reuniones antes de las 9:30 ni después de las 17:00.
- Prefiero concentrar reuniones en martes y jueves si es posible.
- Los lunes y miércoles deberían ser mis días de "maker" (máximo
  2 reuniones cada uno).

Analiza la semana y:

1. ESTADO ACTUAL: ¿se respetan mis reglas? ¿dónde se violan?

2. PROPUESTA DE REORGANIZACIÓN:
   - Reuniones que podrían moverse a martes/jueves.
   - Para cada movimiento: email al organizador proponiendo nuevo horario.

3. BLOQUES DE FOCO:
   - Crea eventos bloqueadores en mi calendario titulados
     "🔒 Trabajo concentrado — No agendar" en los huecos protegidos.
   - Mínimo 2 horas cada bloque.

4. DEFENSA PROACTIVA:
   - Genera un mensaje para mi equipo explicando mi política
     de bloques de foco.
   - Configura un texto de auto-rechazo para invitaciones que caigan
     en mis bloques protegidos.

Muéstrame el calendario "antes" y "después" de los cambios.
```

---

## Ejercicio 12: Gestionar tareas delegadas

**Prerequisitos:** Haber delegado tareas a otros miembros del equipo (ver Capítulo 11, Ejercicio 8) o tener una lista de tareas asignadas a otros.

**Contexto:** Delegar no es "enviar y olvidar". Este prompt te ayuda a hacer seguimiento de todo lo que delegaste, detectar tareas atascadas y generar los recordatorios necesarios sin ser agresivo.

```text
Revisa mi archivo de tareas y mis emails enviados de las últimas
2 semanas para identificar todas las tareas que he delegado a otros.

Para cada tarea delegada, muéstrame:

| Tarea | Delegada a | Fecha | Plazo | Estado | Última comunicación |

Los estados posibles son:
- ✅ Completada (me confirmaron que está hecha)
- 🟡 En curso (hay evidencia de avance)
- 🔴 Sin respuesta (no he recibido actualización)
- ⚠️ Retrasada (pasó el plazo sin entregable)

Para las tareas en estado 🔴 o ⚠️, genera un email de seguimiento
para cada persona. Reglas del email:
- Tono amable pero directo. No pasivo-agresivo.
- Recordar el compromiso original y el plazo.
- Preguntar si hay algún bloqueo en el que pueda ayudar.
- Proponer una nueva fecha si el plazo original ya pasó.
- Máximo 5 líneas.

Además, genera una tabla resumen de "salud de delegación":
- ¿Qué porcentaje de tareas delegadas se entregan a tiempo?
- ¿Quién cumple mejor y quién necesita más seguimiento?
- ¿Hay tareas que debería recuperar y hacer yo mismo?

Actualiza mi archivo de tareas con el estado actual de cada
tarea delegada.
```

---

## Notas para el lector

Estos ejercicios forman un sistema completo de gestión del tiempo. Los ejercicios 2, 9 y 10 (planificación semanal, revisión diaria y revisión del viernes) son los tres rituales que, aplicados de forma consistente, transforman la relación con el calendario y las tareas.

El archivo de tareas en Markdown (Ejercicio 4) es deliberadamente simple. No necesitas una herramienta sofisticada: un archivo de texto que el agente pueda leer y actualizar es suficiente para la mayoría de los profesionales.
