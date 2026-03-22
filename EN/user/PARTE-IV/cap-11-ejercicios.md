# Capítulo 11 — Email inteligente: triaje, respuesta y gestión de bandeja de entrada

Ejercicios prácticos con prompts listos para copiar y pegar en Claude Code o Claude Desktop. Todos los ejercicios asumen que tienes acceso a tu cuenta de correo a través de MCP (Gmail, Outlook) o que pegas los emails manualmente en la conversación.

---

## Ejercicio 1: Verificar la conexión con Gmail

**Prerequisitos:** Tener configurado el servidor MCP de Gmail en Claude Desktop o Claude Code.

**Contexto:** Antes de lanzar cualquier flujo de trabajo con email, confirma que el agente puede leer tu bandeja de entrada. Este prompt verifica la conexión y muestra un resumen básico para que compruebes que los datos son correctos.

```text
Verifica que tienes acceso a mi cuenta de Gmail.
Muéstrame:
1. La dirección de correo conectada
2. Las etiquetas disponibles en mi cuenta
3. Los 5 emails más recientes de la bandeja de entrada (asunto, remitente, fecha)
4. El número total de emails no leídos

Si algo falla, explícame qué está fallando y cómo solucionarlo.
```

---

## Ejercicio 2: Clasificación de emails de las últimas 48 horas

**Prerequisitos:** Acceso a la bandeja de entrada (MCP o copia manual de los emails).

**Contexto:** La bandeja de entrada acumula decenas de mensajes al día. Este prompt clasifica todo lo recibido en las últimas 48 horas en tres categorías de acción, para que puedas empezar el día sabiendo exactamente dónde poner tu atención.

```text
Lee todos los emails recibidos en las últimas 48 horas en mi bandeja de entrada.
Clasifica cada uno en exactamente una de estas tres categorías:

- URGENTE: requiere mi respuesta o acción antes de que termine hoy.
  Criterios: plazos explícitos, escalaciones, decisiones bloqueantes,
  mensajes de superiores o clientes con tono de urgencia.

- IMPORTANTE: requiere atención esta semana, pero no hoy.
  Criterios: seguimientos de proyectos, peticiones de colaboración,
  revisiones de documentos, reuniones por confirmar.

- ARCHIVO: no requiere acción por mi parte.
  Criterios: newsletters, notificaciones automáticas, CC informativos,
  hilos donde ya respondió otra persona, publicidad.

Para cada email muéstrame una tabla con:
| Categoría | Remitente | Asunto | Razón de la clasificación | Acción sugerida |

Ordena la tabla con URGENTE primero, luego IMPORTANTE, luego ARCHIVO.
Al final, dame un resumen: cuántos emails hay en cada categoría
y cuánto tiempo estimas que necesito para procesar los urgentes.
```

---

## Ejercicio 3: Generar borradores de respuesta para emails urgentes

**Prerequisitos:** Haber completado el Ejercicio 2 o tener identificados al menos 3 emails urgentes.

**Contexto:** Una vez identificados los emails urgentes, el siguiente paso es preparar borradores de respuesta. El agente no envía nada: genera los textos para que tú los revises, ajustes y envíes. Esto reduce el tiempo de respuesta de minutos a segundos por email.

```text
De los emails clasificados como URGENTE, selecciona los 3 más críticos.
Para cada uno, genera un borrador de respuesta que cumpla estas reglas:

1. Tono profesional pero cercano, en español.
2. Máximo 150 palabras por respuesta (nadie lee emails largos).
3. Estructura:
   - Línea de apertura que acuse recibo del tema.
   - Respuesta directa a lo que se pide.
   - Si necesito más información, preguntar de forma concreta (no genérica).
   - Cierre con próximo paso claro y fecha si aplica.
4. Si el email requiere una decisión que no puedes tomar por mí,
   indícalo claramente: "[DECISIÓN NECESARIA: ...]"

Muéstrame cada borrador con el formato:

### Email N: [Asunto original]
**De:** [remitente]
**Contexto:** [resumen en 1 línea de qué trata]
**Borrador de respuesta:**
[texto del borrador]
**Notas para revisión:** [qué debería verificar antes de enviar]
```

---

## Ejercicio 4: Redactar un email complejo desde cero

**Prerequisitos:** Ninguno especial. Este ejercicio funciona con cualquier herramienta de Claude.

**Contexto:** No todos los emails son respuestas. A veces necesitas redactar un mensaje delicado desde cero: una negociación, una mala noticia, una petición difícil. Este prompt simula un caso real donde debes comunicar a un proveedor una reducción del 30% en pedidos.

```text
Necesito redactar un email a un proveedor con el que llevamos 4 años
trabajando. La situación:

- Vamos a reducir los pedidos un 30% a partir del próximo trimestre.
- La razón es una reestructuración interna de nuestra cadena de suministro,
  NO un problema con su servicio (que ha sido excelente).
- Queremos mantener la relación comercial a largo plazo.
- Necesitamos negociar nuevas condiciones de precio unitario,
  porque al reducir volumen perderemos el descuento actual por cantidad.
- El contacto se llama Marta Fernández, directora comercial.

Genera el email con estas características:
1. Asunto que no suene alarmista.
2. Apertura que reconozca la buena relación.
3. Explicación honesta de la situación (sin dar detalles internos
   confidenciales).
4. Propuesta concreta: reunión la próxima semana para revisar condiciones.
5. Cierre que refuerce el compromiso a largo plazo.
6. Tono: firme pero respetuoso. No pedir disculpas excesivas
   ni sonar condescendiente.

Genera DOS versiones:
- Versión A: formal (para enviar desde dirección de compras).
- Versión B: más cercana (si yo tengo relación personal con Marta).

Para cada versión, indícame los puntos débiles
que debería reforzar antes de enviar.
```

---

## Ejercicio 5: Gestionar un hilo de email complejo

**Prerequisitos:** Un hilo de email largo (12+ mensajes). Puedes pegarlo directamente en la conversación o adjuntar las capturas.

**Contexto:** Los hilos largos son agotadores de leer. Pierdes el contexto, no sabes quién dijo qué, y las decisiones se diluyen entre réplicas. Este prompt extrae toda la información relevante y te posiciona para actuar sin releer 12 mensajes.

```text
Analiza este hilo de correo electrónico que tiene 12 mensajes
entre varias personas.

Necesito que extraigas:

1. CRONOLOGÍA: tabla con fecha, remitente y resumen de cada mensaje
   (máximo 1 línea por mensaje).

2. PARTICIPANTES: quién es cada persona y qué rol juega en la conversación
   (decisor, técnico, intermediario, solo informado).

3. DECISIONES TOMADAS: lista de cada decisión explícita que se haya
   acordado en el hilo, con la fecha y quién la tomó.

4. COMPROMISOS ABIERTOS: qué prometió cada persona que aún no se ha
   cumplido o confirmado.

5. PUNTOS DE DESACUERDO: dónde hay posiciones encontradas o temas
   sin resolver.

6. MI SITUACIÓN: basándote en los mensajes, dime qué se espera de mí
   exactamente, qué plazos tengo y qué información me falta.

7. BORRADOR DE RESPUESTA: genera un email que cierre los temas abiertos
   que dependen de mí y pida clarificación sobre los que no tengo
   información suficiente.

Formato: usa tablas y listas. Sé conciso pero no omitas nada relevante.
```

---

## Ejercicio 6: Análisis de patrones de la bandeja de entrada

**Prerequisitos:** Acceso a la bandeja de entrada del último mes (MCP o exportación).

**Contexto:** Antes de optimizar tu flujo de email, necesitas entender tus patrones actuales. Este prompt convierte tu bandeja en datos: quién te escribe más, qué temas dominan, cuándo recibes más carga y dónde pierdes tiempo.

```text
Analiza todos los emails de mi bandeja de entrada del último mes completo.
Genera un informe de patrones que incluya:

1. VOLUMEN:
   - Total de emails recibidos y enviados.
   - Media diaria y desviación (¿hay días pico?).
   - Distribución por día de la semana y franja horaria.

2. REMITENTES PRINCIPALES:
   - Top 10 personas que más me escriben, con número de emails.
   - Top 5 dominios externos más frecuentes.
   - ¿Cuántos emails son de personas vs. sistemas automáticos?

3. TIEMPOS DE RESPUESTA:
   - Mi tiempo medio de respuesta (si se puede calcular).
   - Emails que tardé más de 48h en responder.
   - Emails que nunca respondí.

4. TEMAS DOMINANTES:
   - Agrupa los emails por tema o proyecto (usa los asuntos y contenido).
   - ¿Qué porcentaje de mi bandeja es cada tema?

5. CANDIDATOS A AUTOMATIZACIÓN:
   - Emails repetitivos que siguen un patrón predecible.
   - Newsletters o notificaciones que podría filtrar automáticamente.
   - Hilos donde soy CC pero nunca participo.

6. RECOMENDACIONES:
   - 3 reglas de filtro concretas que me ahorrarían tiempo.
   - 3 respuestas tipo que podría tener como plantilla.
   - 1 hábito que debería cambiar basándote en los datos.

Presenta el informe con gráficos en texto (barras ASCII o similares)
donde sea útil para visualizar tendencias.
```

---

## Ejercicio 7: Respuesta a email de negociación con contrapropuestas

**Prerequisitos:** Un email recibido con una propuesta comercial, de precios o de condiciones. Puedes usar uno real o el siguiente escenario ficticio.

**Contexto:** Responder a una negociación por email es un arte. No puedes ser demasiado agresivo ni demasiado blando. Este prompt genera tres opciones de respuesta con diferentes niveles de firmeza, para que elijas la que mejor se adapte a tu situación.

```text
He recibido un email de un cliente que quiere renovar el contrato anual
de servicio, pero pide una rebaja del 15% sobre el precio actual.
Su argumento es que "el mercado ha bajado" y que tiene otra oferta
más barata de un competidor.

Nuestro contexto interno (NO compartir con el cliente):
- El coste real de servir a este cliente ha subido un 8% por inflación.
- El cliente representa el 12% de nuestra facturación anual.
- Perderlo sería doloroso pero no catastrófico.
- Podemos ofrecer hasta un 5% de descuento sin perder margen.
- Tenemos un servicio premium nuevo que podríamos ofrecerle como valor añadido.

Genera TRES contrapropuestas diferentes:

OPCIÓN A — FIRME:
- No aceptamos rebaja.
- Justificación basada en valor entregado y coste real.
- Tono profesional y seguro.

OPCIÓN B — FLEXIBLE:
- Ofrecemos el 5% máximo, pero vinculado a compromiso de 2 años.
- Incluimos acceso al servicio premium como incentivo.
- Tono colaborativo.

OPCIÓN C — CREATIVA:
- No tocamos el precio base.
- Reestructuramos el servicio para que el cliente perciba más valor.
- Proponemos un modelo diferente (pago por uso, paquete ampliado, etc.).
- Tono innovador.

Para cada opción:
1. El email completo, listo para enviar.
2. Puntos fuertes y débiles de esa estrategia.
3. Posible reacción del cliente.
4. Mi siguiente movimiento si el cliente rechaza esta opción.
```

---

## Ejercicio 8: Gestión de delegación por email con equipo

**Prerequisitos:** Conocer los nombres y especialidades de tu equipo. Si no tienes equipo real, usa los perfiles ficticios del prompt.

**Contexto:** Cuando gestionas un equipo, gran parte de la coordinación pasa por email. Este prompt te ayuda a delegar tareas de forma clara, con plazos y expectativas explícitas, evitando los malentendidos habituales.

```text
Tengo 5 miembros en mi equipo con estas especialidades:

1. Laura — desarrollo backend (Python, APIs, bases de datos)
2. Miguel — desarrollo frontend (React, TypeScript, UX)
3. Ana — análisis de datos y reporting (SQL, dashboards, Excel avanzado)
4. Pedro — infraestructura y DevOps (Docker, CI/CD, monitorización)
5. Sofía — gestión de proyecto y comunicación con cliente

Acabo de salir de una reunión donde se decidieron estas tareas:
- Migrar la API de autenticación a OAuth 2.0 (plazo: 2 semanas)
- Rediseñar el dashboard de métricas del cliente (plazo: 10 días)
- Generar un informe de rendimiento del último trimestre (plazo: viernes)
- Configurar alertas de monitorización para el nuevo entorno (plazo: 1 semana)
- Preparar la presentación de avance para el cliente (plazo: jueves)

Para cada tarea, genera un email de delegación que incluya:

1. Asunto claro que identifique la tarea.
2. Contexto: por qué es necesaria (2-3 líneas máximo).
3. Entregable esperado: qué exactamente debe producir.
4. Plazo: fecha y hora concretas.
5. Dependencias: si necesita algo de otro miembro del equipo, indicarlo.
6. Criterio de "hecho": cómo sabremos que la tarea está completada.
7. Checkpoint: una fecha intermedia para verificar avance.

Además, genera un email resumen para todo el equipo que muestre:
- Quién hace qué
- Tabla de plazos
- Dependencias cruzadas
- Próxima reunión de seguimiento propuesta
```

---

## Ejercicio 9: Resumen semanal de email

**Prerequisitos:** Acceso a la bandeja de entrada de la última semana (MCP o exportación).

**Contexto:** Cada viernes, antes de desconectar, necesitas saber si dejas cabos sueltos. Este prompt genera un resumen ejecutivo de toda tu actividad de email de la semana: qué resolviste, qué queda pendiente y qué debería ser lo primero el lunes.

```text
Analiza todos los emails enviados y recibidos durante esta semana
(de lunes a hoy).

Genera un resumen semanal con esta estructura:

## 1. RESUELTO ESTA SEMANA
- Lista de hilos o temas que se cerraron con éxito.
- Para cada uno: una línea con el resultado o decisión final.

## 2. PENDIENTE (requiere acción mía)
- Emails que recibí y aún no he respondido.
- Compromisos que adquirí por email y aún no he cumplido.
- Para cada uno: urgencia (alta/media/baja) y acción concreta necesaria.

## 3. ESPERANDO RESPUESTA DE OTROS
- Emails que envié y aún no me han contestado.
- Para cada uno: a quién escribí, hace cuántos días y si debo hacer
  seguimiento.

## 4. ALERTAS
- Hilos que se están complicando o donde detecto tensión.
- Plazos que vencen la próxima semana.
- Personas que me escribieron varias veces sin obtener respuesta.

## 5. PLAN PARA EL LUNES
- Las 3 primeras acciones de email que debería hacer el lunes,
  ordenadas por impacto.
- Borradores sugeridos para los 2 emails más urgentes pendientes.

Formato: usa tablas donde mejore la legibilidad.
Sé directo: no necesito introducción ni despedida, solo la información.
```

---

## Notas para el lector

Estos ejercicios están diseñados para ejecutarse en orden progresivo: desde verificar la conexión hasta gestionar flujos complejos de comunicación. Cada prompt es autocontenido, pero la combinación de varios (clasificación + respuestas + resumen semanal) es donde se obtiene el mayor ahorro de tiempo.

Adapta siempre los prompts a tu contexto real: nombres, plazos, tono de tu organización y nivel de formalidad que necesites.
