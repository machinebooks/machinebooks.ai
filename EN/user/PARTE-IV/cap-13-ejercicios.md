# Capítulo 13 — Reuniones: preparación, actas, seguimiento y plantillas

Ejercicios prácticos con prompts listos para copiar y pegar en Claude Code o Claude Desktop. Estos ejercicios cubren el ciclo completo de una reunión: antes (preparación), durante (notas) y después (actas, seguimiento, plantillas reutilizables).

---

## Ejercicio 1: Preparar una reunión con contexto de email

**Prerequisitos:** Acceso al calendario y a la bandeja de entrada (MCP o copia manual). Una reunión programada para mañana o esta semana.

**Contexto:** Llegar a una reunión sin contexto es perder los primeros 10 minutos poniéndote al día. Este prompt cruza la información del calendario con los emails recientes de los asistentes para que llegues preparado con todo el contexto relevante.

```text
Mañana tengo esta reunión:
- Título: [nombre de la reunión]
- Hora: [hora]
- Asistentes: [lista de personas]
- Duración: [minutos]

Prepárame para la reunión:

1. CONTEXTO DE EMAIL:
   - Busca todos los emails intercambiados con los asistentes
     en las últimas 2 semanas.
   - Resume los temas activos con cada persona (máximo 3 líneas
     por persona).
   - Identifica compromisos pendientes: qué les debo yo y qué me
     deben ellos.

2. HISTORIAL:
   - ¿He tenido reuniones previas con estos asistentes? Si encuentras
     información en emails o calendario, resúmela.
   - ¿Hay temas recurrentes o problemas que se arrastran?

3. AGENDA SUGERIDA:
   - Si la reunión no tiene agenda, propón una basada en los temas
     activos detectados.
   - Si tiene agenda, compleméntala con puntos que podrían surgir
     según el contexto.

4. MI PREPARACIÓN:
   - 3 puntos clave que debería llevar preparados.
   - 2 preguntas que debería hacer.
   - 1 dato o documento que debería tener a mano.
   - Posibles temas incómodos que podrían surgir y cómo manejarlos.

5. OBJETIVO:
   - ¿Qué resultado concreto necesito de esta reunión?
   - ¿Cuál es el mínimo aceptable si no consigo todo?
```

---

## Ejercicio 2: Generar acta formal a partir de notas caóticas

**Prerequisitos:** Notas tomadas durante una reunión (pueden ser desordenadas, abreviadas, incompletas). Pégalas directamente en la conversación.

**Contexto:** Las notas que tomas durante una reunión son para ti: abreviaturas, frases sueltas, flechas mentales. El acta es para los demás: clara, estructurada, accionable. Este prompt transforma lo primero en lo segundo.

```text
Acabo de salir de una reunión. Estas son mis notas en bruto
(desordenadas, con abreviaturas, incompletas):

---
[Pega aquí tus notas tal cual las tomaste. Ejemplo:]

reunion proyecto alfa - 14:30
asistentes: marta, jose, yo, ana (se unio tarde)
jose dice q el plazo no es realista - quiere 2 sem más
marta no está de acuerdo, dice q el cliente no espera
yo propuse partir en 2 fases - fase 1 para el plazo original
fase 2 con 2 sem extra
ana dice q hay dependencia con equipo de infraestructura
- necesitan 3 días para el entorno
decidimos: fase 1 para el 15, fase 2 para el 30
jose se encarga de redefinir alcance fase 1
ana habla con infra hoy
marta prepara comunicación al cliente
yo hago seguimiento el viernes
tema presupuesto: quedan 12k de los 50k originales
jose dice q no da para fase 2 con el proveedor actual
marta va a pedir ampliación - necesita justificación por escrito
---

Transforma estas notas en:

## 1. ACTA FORMAL

### Datos de la reunión
| Campo | Valor |
|---|---|
| Reunión | [título] |
| Fecha | [fecha] |
| Asistentes | [lista] |
| Duración | [estimada] |

### Resumen ejecutivo
[3-5 líneas que cualquier persona pueda leer en 30 segundos
y entender qué se decidió]

### Temas tratados
Para cada tema:
- Descripción del tema.
- Posiciones expuestas.
- Decisión tomada (o "pendiente" si no se cerró).

### Tabla de acciones
| # | Acción | Responsable | Plazo | Dependencias |
|---|---|---|---|---|

### Próximos pasos
- Próxima reunión de seguimiento (proponer fecha).
- Qué debe estar listo para esa reunión.

## 2. EMAIL DE SEGUIMIENTO
Genera un email para enviar a todos los asistentes con:
- Agradecimiento breve.
- Resumen de decisiones (3-4 bullets).
- Tabla de acciones con responsables y plazos.
- Fecha de próximo seguimiento.
- Tono profesional, máximo 200 palabras.
```

---

## Ejercicio 3: Seguimiento de acciones de reunión

**Prerequisitos:** Un acta de reunión previa con acciones asignadas (del Ejercicio 2 u otra reunión). Acceso al archivo de tareas.

**Contexto:** Las reuniones generan acciones. Si esas acciones no se integran en tu sistema de tareas, se pierden. Este prompt toma las acciones de un acta y las convierte en tareas rastreables.

```text
Aquí está el acta de la última reunión con sus acciones:

[Pega la tabla de acciones del acta o el acta completa]

Necesito que hagas lo siguiente:

1. INTEGRAR EN MI ARCHIVO DE TAREAS:
   - Añade cada acción que me corresponde a mi archivo de tareas
     (ruta: ~/tareas/tareas-semana.md).
   - Usa el formato estándar con plazo y origen "Reunión [nombre]".
   - Si la acción depende de que otro complete algo primero,
     márcala como "bloqueada por [persona]".

2. CREAR RECORDATORIOS:
   - Para las acciones de otros que me afectan, crea una tarea
     de seguimiento 2 días antes de su plazo.
   - Formato: "Verificar con [persona] el avance de [acción]".

3. GENERAR EMAILS DE SEGUIMIENTO:
   - Si alguna acción tenía plazo esta semana y no he recibido
     confirmación, genera un email de seguimiento amable.
   - Si alguna acción me requiere información que aún no tengo,
     genera un email para solicitarla.

4. VERIFICAR COHERENCIA:
   - ¿Hay acciones que contradicen tareas ya existentes
     en mi archivo?
   - ¿Hay plazos imposibles dada mi carga actual?
   - Si encuentras problemas, propón cómo resolverlos.

Actualiza el archivo de tareas y muéstrame los cambios realizados.
```

---

## Ejercicio 4: Acta de reunión caótica con múltiples participantes

**Prerequisitos:** Notas de una reunión larga y compleja. Este ejercicio incluye un escenario de ejemplo que puedes sustituir por una reunión real.

**Contexto:** Las reuniones más difíciles de documentar son las que involucran a muchas personas, temas cruzados y discusiones acaloradas. Este prompt maneja ese caos y extrae estructura donde no la hay.

```text
Acabo de sobrevivir a una reunión de 2 horas con 6 personas
sobre el presupuesto del próximo trimestre. Fue caótica.
Aquí están mis notas:

---
[Pega tus notas o usa este ejemplo:]

Reunión presupuesto Q2 - 2h - sala grande
Personas: Director Financiero (DF), Dir. Comercial (DC),
Dir. Tecnología (DT), yo, PM Laura, Controller Eva

DF abre: hay que recortar 15% del presupuesto total
DC protesta: si recortamos comercial, caen las ventas
DT dice que infra no se puede tocar - servidores al límite
yo propongo: recortar en licencias sw que no usamos - 8% ahorro potencial
Eva confirma: hay 23 licencias activas, solo 14 se usan regularmente
DC quiere mantener herramienta CRM premium
DF: CRM se queda, pero el resto de licencias se revisan

Laura propone plan de revisión en 2 fases:
  fase 1 (2 sem): auditoría completa de licencias
  fase 2 (4 sem): renegociar contratos

discusión sobre cloud: DT quiere migrar a reservas anuales
- ahorro estimado 22% vs. pago por uso actual
- DF preocupado por el compromiso a 1 año
- acuerdan: DT prepara propuesta detallada para la próxima reunión

tema viajes: DC pide mantener presupuesto de viajes comerciales
- DF propone reducir 30%
- acuerdan 20% de reducción y revisar en 6 meses

presupuesto formación: yo pido mantenerlo, es inversión no gasto
- DF acepta mantener pero pide justificación ROI por curso
- debo enviar el análisis la próxima semana

Eva cierra con los números: falta recortar un 4% adicional
- DF pide que cada director proponga dónde recortar ese 4%
  en su área antes del viernes
---

Genera el acta completa con:

### Resumen ejecutivo
[Para alguien que no estuvo: qué se decidió en 5 líneas]

### Temas tratados con detalle
Para cada tema:
- Las posiciones de cada participante.
- Los argumentos a favor y en contra.
- La decisión final o el estado (abierto/cerrado).

### Tabla de acciones
| # | Acción | Responsable | Plazo | Estado |
[Incluir TODAS las acciones, incluso las implícitas]

### Tabla de presupuesto
[Si hay números, organízalos en una tabla clara con:
partida, presupuesto actual, recorte propuesto, nuevo presupuesto]

### Puntos de tensión
[Identificar dónde hubo desacuerdo y si se resolvió o no]

### Email de seguimiento
[Borrador para enviar a todos los asistentes]
```

---

## Ejercicio 5: Reunión con cliente — doble versión (interna y externa)

**Prerequisitos:** Notas de una reunión con un cliente externo.

**Contexto:** Cuando te reúnes con un cliente, necesitas dos documentos diferentes: uno interno (con tus impresiones, riesgos y estrategia) y otro externo (el acta que compartes con el cliente, más formal y cuidada). Este prompt genera ambos.

```text
Acabo de tener una reunión con un cliente. Estas son mis notas:

[Pega tus notas o usa este ejemplo:]

Reunión con cliente MegaCorp - revisión trimestral
Asistentes: Patricia (directora de proyecto cliente), Raúl (técnico
cliente), yo, Laura (PM nuestro equipo)

Patricia contenta con los resultados del último sprint
pero preocupada por los tiempos del módulo de reporting
- dice que su jefe presiona por tenerlo antes de julio
- nosotros sabemos que julio es muy justo (Laura dice agosto
  realista)
yo le dije que "haríamos todo lo posible" (no me comprometí
a julio)
Raúl tiene problemas de integración con su API interna
- necesita documentación de nuestra API actualizada
- Laura se compromete a enviársela el lunes

tema nuevo: Patricia pregunta por módulo de IA predictiva
- no estaba en el alcance original
- ella dice que "lo mencionamos en la propuesta"
- yo no recuerdo eso — revisar propuesta original
- le dije que lo analizaríamos y enviaríamos valoración

sensación general: contentos pero empujando para más scope
sin más presupuesto
---

Genera DOS documentos:

## VERSIÓN INTERNA (solo para nuestro equipo)

### Situación del cliente
- Nivel de satisfacción real (no lo que dicen, lo que interpretas).
- Riesgos detectados.
- Señales de que están pidiendo más sin pagar.

### Análisis de peticiones
- Módulo reporting: ¿es factible en julio? Argumentos para negociar
  un plazo realista.
- Módulo IA predictiva: ¿estaba en la propuesta o no? Cómo manejar
  si no estaba (cobrar) o si estaba (cumplir).

### Estrategia para la próxima reunión
- Mensajes clave que debemos transmitir.
- Líneas rojas que no debemos cruzar.
- Concesiones que podemos hacer sin impacto.

### Acciones internas
| Acción | Responsable | Plazo |

## VERSIÓN EXTERNA (para enviar al cliente)

### Acta de reunión
- Formato profesional y diplomático.
- Solo incluir lo acordado, no nuestras dudas internas.
- Tabla de acciones con compromisos de ambas partes.
- Próximos pasos claros.
- Tono: positivo, profesional, sin prometer nada que no hayamos
  acordado explícitamente.
- Máximo 1 página.
```

---

## Ejercicio 6: Preparar reunión semanal recurrente

**Prerequisitos:** Una reunión semanal de equipo que se repite. Acceso al calendario, email y archivo de tareas.

**Contexto:** Las reuniones semanales de equipo pueden ser las más útiles o las más inútiles de la semana. La diferencia está en la preparación. Este prompt genera automáticamente la agenda basándose en lo que ocurrió durante la semana.

```text
Mañana tengo la reunión semanal de equipo. Es recurrente,
todos los [día] a las [hora], con [lista de asistentes].

Prepara la agenda de esta semana basándote en:

1. PROGRESO DESDE LA ÚLTIMA REUNIÓN:
   - Revisa las acciones de la reunión anterior
     [pega el acta anterior o indica dónde encontrarla].
   - Para cada acción: ¿se completó? ¿hay evidencia en emails
     o en el archivo de tareas?

2. TEMAS NUEVOS:
   - Emails importantes del equipo esta semana que requieren
     discusión grupal.
   - Tareas bloqueadas que necesitan decisión colectiva.
   - Alertas o riesgos que surgieron.

3. AGENDA PROPUESTA:
   | # | Tema | Responsable | Tiempo | Tipo |
   Tipos: informativo (solo escuchar), decisión (votar/acordar),
   discusión (explorar opciones), seguimiento (verificar avance).

   Reglas:
   - Máximo 6 temas (si hay más, prioriza y mueve el resto
     a "parking lot").
   - Total no debe superar [duración de la reunión].
   - Los temas de decisión van primero (cuando la energía es alta).
   - Los informativos van al final (o se envían por email antes).

4. MATERIAL PREVIO:
   - ¿Qué deberían leer los asistentes antes de la reunión?
   - Genera un email breve con la agenda y el material adjunto
     para enviar hoy.

5. PLANTILLA DE NOTAS:
   - Genera una plantilla vacía para tomar notas durante la reunión,
     con los temas y espacio para decisiones y acciones.
```

---

## Ejercicio 7: Trabajar con transcripciones largas de videollamada

**Prerequisitos:** Una transcripción de Zoom, Teams o Meet (suelen ser archivos .vtt, .txt o .docx). Las transcripciones automáticas tienen errores, nombres mal escritos y falta de puntuación.

**Contexto:** Las transcripciones automáticas de videollamada son largas, ruidosas y difíciles de leer. Pero contienen todo lo que se dijo. Este prompt extrae la información útil de una transcripción de 1-2 horas y la convierte en un documento accionable.

```text
Adjunto la transcripción automática de una videollamada de [duración].
La transcripción tiene errores típicos: nombres mal escritos,
puntuación incorrecta, fragmentos incoherentes donde alguien
habló encima de otro.

Los participantes reales son:
- [Lista de nombres correctos y sus roles]

Necesito que proceses la transcripción y generes:

## 1. RESUMEN EJECUTIVO (máximo 10 líneas)
Para alguien que no estuvo en la reunión.

## 2. TRANSCRIPCIÓN LIMPIA POR BLOQUES TEMÁTICOS
No quiero la transcripción completa, sino los temas principales
organizados:
- Tema: [nombre del tema]
- Quién habló: [personas]
- Puntos clave: [bullet points con lo importante]
- Decisión: [si la hubo]
- Citas textuales relevantes: [solo si alguien dijo algo literal
  que importa conservar]

## 3. TABLA DE ACCIONES
| # | Acción | Responsable | Plazo (si se mencionó) |

## 4. MOMENTOS CLAVE
- Momentos de acuerdo importante (con timestamp si lo hay).
- Momentos de desacuerdo o tensión.
- Información nueva que cambió la conversación.
- Promesas o compromisos verbales de cada participante.

## 5. ACTA FORMAL
Genera el acta lista para distribuir, basándote en los bloques
anteriores.

## 6. EMAIL DE SEGUIMIENTO
Borrador para enviar a todos los participantes.

Reglas:
- Corrige los nombres según la lista que te di.
- Ignora las partes sociales (saludos, "¿me oís bien?", etc.).
- Si algo es ambiguo, indícalo con [VERIFICAR: ...].
- Si detectas que falta contexto o hay contradicciones, avísame.
```

---

## Ejercicio 8: Plantillas reutilizables para tipos de reunión

**Prerequisitos:** Ninguno especial. Este ejercicio genera artefactos que guardarás para uso repetido.

**Contexto:** No todas las reuniones son iguales. Una reunión de seguimiento de proyecto no tiene la misma estructura que una sesión de brainstorming o una revisión de incidencia. Este prompt crea plantillas específicas para tus tipos de reunión más frecuentes.

```text
Quiero crear un sistema de plantillas de acta para mis reuniones
recurrentes. Tengo estos tipos de reunión habituales:

1. REUNIÓN DE SEGUIMIENTO DE PROYECTO (semanal, 30-45 min)
2. REVISIÓN CON CLIENTE (quincenal o mensual, 60 min)
3. SESIÓN DE BRAINSTORMING / DISEÑO (puntual, 60-90 min)
4. REUNIÓN DE INCIDENCIA / POST-MORTEM (puntual, 30-60 min)
5. ONE-ON-ONE CON MIEMBRO DEL EQUIPO (semanal, 30 min)

Para cada tipo, genera una plantilla Markdown que incluya:

### Cabecera estándar
- Título, fecha, asistentes, duración.

### Secciones específicas del tipo de reunión
(diferentes para cada tipo — no una plantilla genérica)

### Tabla de acciones
(formato común para todos los tipos)

### Sección de notas libres

### Instrucciones de uso
- Breve indicación de cómo llenar cada sección.
- Qué secciones son obligatorias y cuáles opcionales.

Guarda cada plantilla en un archivo separado:
- ~/reuniones/plantillas/seguimiento-proyecto.md
- ~/reuniones/plantillas/revision-cliente.md
- ~/reuniones/plantillas/brainstorming.md
- ~/reuniones/plantillas/post-mortem.md
- ~/reuniones/plantillas/one-on-one.md

Además, genera un archivo índice (~/reuniones/plantillas/README.md)
que explique cuándo usar cada plantilla.
```

---

## Ejercicio 9: Buscar en historial de actas de reuniones

**Prerequisitos:** Varias actas de reuniones guardadas en una carpeta (formato Markdown o texto). Si no las tienes, este prompt funciona igualmente con emails de seguimiento de reuniones pasadas.

**Contexto:** Después de meses de reuniones, necesitas encontrar "aquella decisión que tomamos en septiembre" o "quién se comprometió a hacer X". Este prompt busca en tu historial de actas como un buscador especializado.

```text
Tengo actas de reuniones guardadas en la carpeta ~/reuniones/actas/
(también puedo tener información en mis emails de seguimiento).

Necesito buscar información específica en el historial.
Responde estas consultas:

1. "¿Cuándo decidimos cambiar el proveedor de hosting
   y quién propuso el cambio?"
   → Busca en todas las actas referencias a hosting, infraestructura
   o proveedor cloud.

2. "¿Qué compromisos tiene pendientes [nombre de persona]?"
   → Busca todas las acciones asignadas a esa persona en actas
   recientes que no tengan marca de completado.

3. "¿Cuántas veces hemos discutido el tema de [tema X]
   en los últimos 3 meses?"
   → Lista cada mención con fecha, reunión y qué se dijo/decidió.

4. "¿Qué decidimos sobre el presupuesto en la reunión del [fecha]?"
   → Busca el acta específica y extrae las decisiones.

Si no encuentras la información exacta, dime:
- Dónde buscaste.
- Qué encontraste que se aproxima.
- Qué información adicional necesitarías para responder.

Formato de respuesta para cada consulta:
- Fuente: [archivo o email donde encontraste la información]
- Fecha: [cuándo se decidió/discutió]
- Contexto: [resumen breve]
- Cita: [texto relevante del acta, si es útil]
```

---

## Notas para el lector

El ciclo completo de una reunión productiva tiene tres fases: preparar (Ejercicios 1, 5, 6, 7), documentar (Ejercicios 2, 4, 7) y dar seguimiento (Ejercicios 3, 9). Si solo puedes adoptar un hábito, que sea generar el acta con tabla de acciones inmediatamente después de la reunión (Ejercicio 2). La disciplina de "no salir de la reunión sin acciones claras" transforma la efectividad de cualquier equipo.

Las plantillas (Ejercicio 8) ahorran tiempo de forma acumulativa: invierte 30 minutos en crearlas y recuperarás ese tiempo en cada reunión durante meses.
