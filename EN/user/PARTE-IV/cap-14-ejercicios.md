# Capítulo 14 — Gestión de proyectos: reportes, riesgos, decisiones y seguimiento

Ejercicios prácticos con prompts listos para copiar y pegar en Claude Code o Claude Desktop. Estos ejercicios asumen que gestionas uno o varios proyectos y que tu información está dispersa en diferentes fuentes: repositorios de código, emails, archivos locales y herramientas de gestión.

---

## Ejercicio 1: Primer informe semanal cruzando múltiples fuentes

**Prerequisitos:** Acceso a un repositorio de GitHub (MCP o enlace), bandeja de entrada y archivos locales del proyecto (notas, documentos, hojas de cálculo).

**Contexto:** El informe semanal de proyecto es el documento más consultado y más odiado. Odiado porque recopilarlo es tedioso. Consultado porque es la única vista consolidada del proyecto. Este prompt automatiza la recopilación cruzando tres fuentes.

```text
Necesito generar el informe semanal de mi proyecto. Tienes acceso
a estas fuentes:

1. GITHUB: repositorio [nombre o URL del repo]
   - Revisa los commits de la última semana.
   - Revisa las pull requests (abiertas, cerradas, en revisión).
   - Revisa las issues (nuevas, cerradas, bloqueadas).

2. EMAIL: mi bandeja de entrada
   - Busca emails relacionados con el proyecto (usa el nombre del
     proyecto o los nombres de los miembros del equipo como filtro).
   - Identifica decisiones, problemas reportados o cambios de alcance.

3. ARCHIVOS LOCALES: carpeta [ruta de tu carpeta de proyecto]
   - Revisa documentos modificados esta semana.
   - Busca notas de reuniones recientes.
   - Si hay un archivo de tareas, inclúyelo.

Con toda esta información, genera el informe semanal:

## Informe semanal — [Nombre del proyecto]
**Período:** [lunes] a [viernes]
**Autor:** [tu nombre]

### Estado general: 🟢 / 🟡 / 🔴
[Una línea explicando por qué ese estado]

### Progreso esta semana
| Área | Completado | En curso | Bloqueado |
|---|---|---|---|
| Desarrollo | [PRs merged] | [PRs abiertas] | [issues bloqueadas] |
| Gestión | [decisiones tomadas] | [temas abiertos] | [riesgos] |

### Hitos
| Hito | Fecha objetivo | Estado | Comentario |
|---|---|---|---|

### Logros principales
- [3-5 bullets con lo más relevante de la semana]

### Problemas y riesgos
| Problema | Impacto | Acción propuesta | Responsable |

### Plan para la próxima semana
- [3-5 prioridades]

### Métricas (si aplica)
- Commits: [número]
- PRs cerradas: [número]
- Issues resueltas: [número]
- Cobertura de tests: [si está disponible]
```

---

## Ejercicio 2: Detección proactiva de riesgos

**Prerequisitos:** Acceso a GitHub (issues, PRs), bandeja de entrada y, opcionalmente, un tablero de tareas.

**Contexto:** Los problemas de proyecto no aparecen de golpe: se anuncian con señales débiles. Una issue que lleva 10 días sin actividad. Una PR sin revisor. Un email con tono tenso. Este prompt busca esas señales y te alerta antes de que se conviertan en crisis.

```text
Analiza el estado actual de mi proyecto buscando señales de riesgo
en todas las fuentes disponibles.

## 1. TICKETS ESTANCADOS
Busca en GitHub issues que:
- Llevan más de 7 días sin actividad (sin comentarios ni commits).
- Están asignadas pero sin evidencia de avance.
- Tienen etiqueta de alta prioridad pero llevan más de 3 días abiertas.
- No tienen asignado a nadie.
Para cada una: resumen, días sin actividad, último responsable.

## 2. PULL REQUESTS SIN REVISAR
Busca PRs que:
- Llevan más de 48 horas sin revisión.
- Tienen cambios solicitados pero sin respuesta del autor.
- Son grandes (>500 líneas) y no tienen ningún comentario.
Para cada una: título, autor, días abierta, revisor asignado (o falta).

## 3. EMAILS PREOCUPANTES
Busca en los emails del proyecto:
- Mensajes con tono de urgencia o frustración.
- Peticiones de escalación.
- Quejas de cliente o stakeholder.
- Cambios de plazo o alcance mencionados.
Para cada uno: remitente, asunto, resumen del problema.

## 4. PATRONES DE RIESGO
Analiza el conjunto y detecta:
- ¿Hay una persona del equipo que aparece como cuello de botella
  en múltiples hilos?
- ¿Hay un módulo o componente que concentra los problemas?
- ¿Hay señales de scope creep (el alcance crece sin control)?
- ¿Los plazos originales siguen siendo realistas?

## 5. MAPA DE RIESGOS
| # | Riesgo | Probabilidad | Impacto | Señales detectadas | Acción propuesta |
Alta/Media/Baja para probabilidad e impacto.

## 6. RECOMENDACIONES INMEDIATAS
Las 3 acciones que debería tomar HOY para mitigar los riesgos
más graves. Para cada una, genera el borrador de email o mensaje
correspondiente.
```

---

## Ejercicio 3: Seguimiento de compromisos entre fuentes

**Prerequisitos:** Acceso a email, actas de reuniones y sistema de issues/tareas. El valor de este ejercicio crece con el número de fuentes disponibles.

**Contexto:** Los compromisos de proyecto nacen en muchos sitios: en un email alguien dice "lo tengo para el viernes", en una reunión se asigna una tarea, en un issue de GitHub alguien se asigna un bug. Si no cruzas las fuentes, los compromisos se pierden entre los sistemas.

```text
Necesito un inventario completo y actualizado de TODOS los
compromisos activos del proyecto, cruzando todas las fuentes.

Busca compromisos en:
1. EMAILS: promesas explícitas ("lo tengo para el viernes",
   "me encargo yo", "te envío mañana").
2. ACTAS DE REUNIONES: acciones asignadas en reuniones recientes
   [indica la carpeta de actas o pega las últimas].
3. GITHUB: issues asignadas, PRs en curso, comentarios con
   compromisos de fecha.
4. ARCHIVO DE TAREAS: [ruta del archivo si lo tienes].

Para cada compromiso encontrado, muéstrame:

| Compromiso | Quién | Origen | Fecha compromiso | Estado | Evidencia |

Estados posibles:
- ✅ Cumplido (hay evidencia de entrega).
- 🟡 En curso (hay actividad pero no está terminado).
- 🔴 Vencido (pasó la fecha y no hay evidencia de entrega).
- ❓ Sin verificar (no hay información suficiente).

Luego genera:

### ANÁLISIS DE FIABILIDAD
- ¿Quién cumple consistentemente?
- ¿Quién tiene compromisos vencidos repetidamente?
- ¿Hay compromisos que nadie está siguiendo?

### ACCIONES DE SEGUIMIENTO
Para cada compromiso en estado 🔴 o ❓, genera un email
o mensaje de seguimiento apropiado.

### COMPROMISOS MÍOS
Lista aparte de todos MIS compromisos con su estado,
para que me asegure de no ser yo quien falla.
```

---

## Ejercicio 4: Dashboard de proyecto desde archivos Markdown

**Prerequisitos:** Archivos del proyecto en formato Markdown, texto o cualquier formato legible. No necesitas herramientas de gestión de proyectos; los archivos son tu herramienta.

**Contexto:** No todos los equipos usan Jira o Asana. Muchos gestionan proyectos con archivos de texto, hojas de cálculo y buena voluntad. Este prompt convierte esos archivos dispersos en un dashboard visual y accionable.

```text
Tengo la información de mi proyecto repartida en estos archivos
Markdown dentro de la carpeta ~/proyecto/:

- tareas.md — Lista de tareas con checkboxes
- notas-reuniones/ — Carpeta con actas semanales
- riesgos.md — Lista de riesgos identificados
- decisiones.md — Registro de decisiones tomadas
- equipo.md — Quién hace qué

[Si tus archivos son diferentes, describe cuáles tienes y dónde]

Genera un dashboard de proyecto en formato Markdown que incluya:

## ESTADO GENERAL
- Semáforo del proyecto: 🟢 / 🟡 / 🔴 (con justificación).
- Frase resumen del estado en 1 línea.

## PROGRESO
- Tareas totales / completadas / en curso / pendientes.
- Barra de progreso en texto: [████████░░] 80%
- Tareas completadas esta semana vs. semana anterior.

## PLAZOS
- Próximos 3 hitos con fecha y estado.
- Tareas con plazo en los próximos 7 días.
- Tareas vencidas.

## EQUIPO
- Tabla de carga por persona:
  | Persona | Tareas asignadas | Completadas | En curso | Bloqueadas |

## RIESGOS ACTIVOS
- Top 3 riesgos por impacto, con estado de mitigación.

## ÚLTIMAS DECISIONES
- Las 5 decisiones más recientes del registro.

## ALERTAS
- Cualquier anomalía detectada en los datos.

Guarda el dashboard en ~/proyecto/dashboard.md.
Este archivo se regenerará cada vez que ejecute este prompt,
así que no añadas contenido manual aquí.
```

---

## Ejercicio 5: Preparar comité de dirección con múltiples proyectos

**Prerequisitos:** Información de 3-5 proyectos activos (archivos locales, GitHub, emails). Este prompt puede tardar más en procesar porque analiza múltiples proyectos.

**Contexto:** El comité de dirección quiere una vista de pájaro: cada proyecto en una página, sin excusas ni tecnicismos. Este prompt genera la documentación ejecutiva para 5 proyectos en formato listo para presentar.

```text
Tengo que preparar la presentación para el comité de dirección
de mañana. Gestiono estos 5 proyectos:

1. Proyecto Alfa — Migración de plataforma legacy
   [Fuentes: repo github.com/equipo/alfa, carpeta ~/proyectos/alfa/]
2. Proyecto Beta — Nuevo módulo de analítica
   [Fuentes: repo github.com/equipo/beta, carpeta ~/proyectos/beta/]
3. Proyecto Gamma — Integración con proveedor externo
   [Fuentes: carpeta ~/proyectos/gamma/, emails con asunto "Gamma"]
4. Proyecto Delta — Mejora de rendimiento
   [Fuentes: repo github.com/equipo/delta]
5. Proyecto Epsilon — Formación del equipo en IA
   [Fuentes: carpeta ~/proyectos/epsilon/]

Para cada proyecto, genera UNA página (máximo) con:

### [Nombre del proyecto]
**Estado:** 🟢 / 🟡 / 🔴
**Responsable:** [nombre]
**Avance general:** [██████░░░░] 60%

**Resumen ejecutivo:** [3 líneas máximo. Qué se hizo, qué queda,
qué preocupa]

**Logros del período:**
- [2-3 bullets]

**Riesgos principales:**
| Riesgo | Impacto | Mitigación |

**Próximos hitos:**
| Hito | Fecha | Confianza (alta/media/baja) |

**Necesidades / Peticiones al comité:**
- [Si necesitas decisión, presupuesto o recursos, aquí]

---

Al final, genera una TABLA RESUMEN de todos los proyectos:
| Proyecto | Estado | Avance | Riesgo principal | Próximo hito |

Y una sección de TEMAS TRANSVERSALES:
- Recursos compartidos entre proyectos.
- Dependencias cruzadas.
- Riesgos que afectan a más de un proyecto.
```

---

## Ejercicio 6: Informes adaptados por audiencia

**Prerequisitos:** Información del proyecto suficiente para generar un informe (del Ejercicio 1 o fuentes propias).

**Contexto:** El mismo proyecto necesita contarse de forma diferente según quién escuche. El consejo quiere impacto en negocio. El equipo técnico quiere detalles de implementación. El cliente quiere saber si cumples plazos. Este prompt genera tres versiones del mismo informe.

```text
Tengo la información actualizada de mi proyecto:
[Pega el informe semanal del Ejercicio 1, o describe
el estado actual del proyecto con los datos que tengas]

Genera TRES versiones del informe para audiencias diferentes:

## VERSIÓN DIRECTIVA (para el consejo de dirección o alta gerencia)
- Máximo 1 página.
- Lenguaje de negocio, CERO jerga técnica.
- Foco en: impacto en ingresos/costes, riesgos de negocio,
  plazos de entrega, necesidades de decisión.
- Formato: resumen ejecutivo + tabla de KPIs + 1 gráfico ASCII
  de tendencia.
- Preguntas que podrían hacerme y respuestas preparadas.

## VERSIÓN TÉCNICA (para el equipo de desarrollo)
- Sin límite de extensión razonable.
- Lenguaje técnico preciso.
- Foco en: arquitectura, deuda técnica, métricas de código,
  blockers técnicos, decisiones de diseño pendientes.
- Formato: secciones por componente/módulo + tabla de issues
  + métricas de GitHub.
- Lista de decisiones técnicas que necesito del equipo.

## VERSIÓN CLIENTE (para el cliente o stakeholder externo)
- Máximo 1 página.
- Lenguaje profesional, accesible pero no condescendiente.
- Foco en: entregas completadas, próximos entregables,
  cumplimiento de plazos, valor entregado.
- NO incluir problemas internos, deuda técnica
  ni conflictos de equipo.
- Formato: logros + próximos pasos + tabla de hitos.
- Tono: confianza controlada (ni exceso de optimismo
  ni transparencia brutal).

Para cada versión, indícame:
- Qué información incluiste y por qué.
- Qué información omitiste deliberadamente y por qué.
- El riesgo principal de esa versión (qué podría preguntarme
  la audiencia que no está cubierto).
```

---

## Ejercicio 7: Lecciones aprendidas de 12 semanas de informes

**Prerequisitos:** Informes semanales acumulados de al menos 8-12 semanas (archivos Markdown, Word, emails o cualquier formato).

**Contexto:** Los informes semanales son una mina de oro de información que nadie explota. Después de 12 semanas, tienes datos suficientes para detectar patrones, tendencias y problemas sistémicos. Este prompt convierte tu historial de informes en inteligencia de proyecto.

```text
Tengo los informes semanales de las últimas 12 semanas
del proyecto en la carpeta ~/proyecto/informes/
[o pégalos directamente si son pocos].

Analiza todos los informes y genera un documento de lecciones
aprendidas:

## 1. EVOLUCIÓN DEL PROYECTO
- Línea temporal: cómo cambió el semáforo del proyecto semana a semana.
  Semana 1: 🟢 | Semana 2: 🟢 | ... | Semana 12: 🟡
- ¿Cuándo empezaron los problemas (si los hubo)?
- ¿Hubo mejoras significativas? ¿Qué las causó?

## 2. RIESGOS RECURRENTES
- Riesgos que aparecen en más de 3 informes.
- ¿Se mitigaron o siguen abiertos?
- ¿Hay riesgos que nunca se identificaron hasta que explotaron?

## 3. ESTIMACIONES VS. REALIDAD
- Hitos que se cumplieron a tiempo vs. los que se retrasaron.
- ¿Cuánto se desviaron los plazos de media?
- ¿Hay un patrón? (ej: siempre subestimamos X tipo de tareas)

## 4. PRODUCTIVIDAD DEL EQUIPO
- ¿Hay semanas sistemáticamente más productivas que otras?
- ¿Qué bloquea más al equipo? (dependencias externas, revisiones,
  falta de especificación...)
- ¿Quién aparece más frecuentemente como cuello de botella?

## 5. PATRONES DE COMUNICACIÓN
- Temas que se repiten semana tras semana sin resolverse.
- Decisiones que se tomaron, se revirtieron y se tomaron otra vez.
- Stakeholders que aparecen solo cuando hay problemas.

## 6. LECCIONES CONCRETAS
Para cada lección:
- Qué pasó (hecho).
- Qué aprendimos (insight).
- Qué haríamos diferente la próxima vez (acción).

## 7. RECOMENDACIONES PARA EL SIGUIENTE PROYECTO
- 5 cosas que funcionaron y debemos repetir.
- 5 cosas que fallaron y debemos cambiar.
- 3 herramientas, procesos o hábitos que deberíamos adoptar.
```

---

## Ejercicio 8: Informe semanal automatizado con archivo de instrucciones

**Prerequisitos:** Un archivo de configuración que define cómo quieres tu informe. Este ejercicio crea el archivo de instrucciones y luego lo usa para generar el informe automáticamente cada semana.

**Contexto:** En lugar de escribir el prompt cada semana, define tus instrucciones una vez en un archivo. Luego solo tienes que decir "genera el informe semanal" y el agente sabe exactamente qué hacer, dónde buscar y en qué formato presentarlo.

```text
Crea un archivo de instrucciones para mi informe semanal
en ~/proyecto/informe-instrucciones.md con este contenido:

# Instrucciones para el informe semanal

## Proyecto
- Nombre: [nombre del proyecto]
- Repositorio: [URL de GitHub]
- Carpeta local: [ruta]
- Equipo: [lista de nombres]

## Fuentes de datos
1. GitHub: commits, PRs, issues de la última semana.
2. Email: buscar mensajes con asunto que contenga "[proyecto]"
   o de los miembros del equipo.
3. Archivo de tareas: [ruta del archivo .md]
4. Actas de reuniones: [ruta de la carpeta]
5. Archivo de riesgos: [ruta]

## Formato del informe
- Archivo de salida: ~/proyecto/informes/informe-YYYY-MM-DD.md
- Extensión: máximo 2 páginas.
- Secciones obligatorias: estado general, logros, problemas,
  plan siguiente semana, métricas.
- Incluir tabla de issues cerradas vs. abiertas.
- Incluir tabla de PRs del período.

## Reglas
- El semáforo se calcula así:
  🟢 = todos los hitos a tiempo, sin riesgos altos
  🟡 = algún hito retrasado O riesgo alto pero con mitigación
  🔴 = hito crítico retrasado O riesgo sin mitigar
- Si hay datos que no puedes verificar, indicar [NO VERIFICADO].
- No inventar métricas ni datos.

## Distribución
- Generar email de resumen para: [lista de destinatarios]
- Versión corta (3 bullets) para: [lista de destinatarios ejecutivos]

---

Ahora, usando ese archivo de instrucciones, genera el informe
semanal de esta semana.
```

---

## Ejercicio 9: Registro de decisiones del proyecto

**Prerequisitos:** Acceso a emails, actas de reuniones y documentos del proyecto donde se hayan tomado decisiones.

**Contexto:** Las decisiones de proyecto se toman en reuniones, emails, conversaciones de pasillo y mensajes de chat. Semanas después, nadie recuerda por qué se decidió X o quién lo aprobó. Este prompt crea y mantiene un registro formal de decisiones.

```text
Necesito crear y mantener un registro de decisiones del proyecto.

## PASO 1: RECOPILAR DECISIONES EXISTENTES
Busca en estas fuentes todas las decisiones tomadas en el proyecto
durante los últimos 2 meses:
- Actas de reuniones: [carpeta o pega las actas]
- Emails del proyecto: busca mensajes donde se decidió algo
  ("decidimos", "aprobado", "se acuerda", "vamos con",
  "descartamos").
- Documentos del proyecto: revisa archivos con nombres como
  "propuesta", "diseño", "arquitectura".

## PASO 2: CREAR EL REGISTRO
Para cada decisión encontrada, documéntala con este formato:

### DEC-[NNN]: [Título breve de la decisión]
| Campo | Valor |
|---|---|
| Fecha | [cuándo se tomó] |
| Decisor | [quién la tomó o aprobó] |
| Contexto | [por qué fue necesaria] |
| Opciones consideradas | [qué alternativas había] |
| Decisión | [qué se decidió] |
| Justificación | [por qué esta opción y no otra] |
| Impacto | [a qué afecta] |
| Estado | vigente / revertida / supersedida |
| Origen | [email, reunión, documento donde se tomó] |

## PASO 3: ANÁLISIS
Después de recopilar todas las decisiones:
- ¿Hay decisiones contradictorias entre sí?
- ¿Hay decisiones que se tomaron sin documentar las alternativas?
- ¿Hay áreas del proyecto sin decisiones formales que las necesiten?
- ¿Hay decisiones que deberían revisarse dado el estado actual?

## PASO 4: GUARDAR
Guarda el registro en ~/proyecto/decisiones.md.
Ordena cronológicamente, las más recientes primero.
Añade un índice al inicio con enlaces a cada decisión.

Este archivo se actualizará después de cada reunión importante.
```

---

## Notas para el lector

Estos ejercicios cubren el ciclo completo de gestión de proyectos con un agente de IA: desde el informe semanal rutinario (Ejercicio 1) hasta la inteligencia de proyecto acumulada (Ejercicio 7). La clave es la constancia: un informe semanal bien hecho durante 12 semanas vale mas que cualquier herramienta sofisticada de gestión.

El Ejercicio 8 (archivo de instrucciones) es especialmente importante: define las reglas una vez y luego cada semana solo necesitas un prompt de una linea. Esa es la diferencia entre usar IA como un juguete y usarla como una herramienta de trabajo real.

Los ejercicios de deteccion de riesgos (Ejercicio 2) y registro de decisiones (Ejercicio 9) son los que mas valor aportan a medio plazo, aunque al principio parezcan burocraticos. Cuando alguien pregunte "por que hicimos esto", tendras la respuesta documentada.
