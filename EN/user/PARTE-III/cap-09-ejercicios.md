# Capítulo 9 — Conectar todo: cuando el agente tiene acceso a tus herramientas reales

Ejercicios prácticos para usar Claude con múltiples servidores MCP conectados simultáneamente. El objetivo es experimentar flujos de trabajo reales donde el agente cruza información entre herramientas.

> **Nota:** Estos ejercicios requieren cuentas activas en los servicios mencionados (Gmail, Slack, Jira, Google Drive). Si no usas alguno de ellos, adapta el prompt al servicio equivalente que uses, o practica solo con los que tengas disponibles.

---

## Ejercicio 1: Configurar múltiples servidores MCP

**Requisitos:**
- Claude Code instalado en terminal
- Cuentas activas en al menos 2 de estos servicios: Gmail, Slack, Jira, GitHub, Google Drive
- Tokens de acceso o credenciales para cada servicio

### Paso A — Instalar los servidores MCP

Ejecuta en tu terminal los servidores que necesites. Cada comando registra un servidor MCP en tu configuración local de Claude Code:

```bash
claude mcp add gmail -- npx -y @modelcontextprotocol/server-gmail
claude mcp add google-drive -- npx -y @modelcontextprotocol/server-google-drive
claude mcp add slack --env SLACK_TOKEN=xoxp-tu-token -- npx -y @modelcontextprotocol/server-slack
claude mcp add github --env GITHUB_TOKEN=ghp_tu_token -- npx -y @modelcontextprotocol/server-github
claude mcp add jira --env JIRA_URL=https://tu-empresa.atlassian.net --env JIRA_EMAIL=tu@email.com --env JIRA_API_TOKEN=tu-token -- npx -y @modelcontextprotocol/server-jira
```

> **Importante:** Sustituye cada token y URL por tus credenciales reales. Nunca compartas estos tokens ni los subas a un repositorio.

### Paso B — Verificar la conexión

Después de añadir los servidores, abre Claude Code y pregunta:

```text
¿Qué herramientas MCP tengo disponibles? Muéstrame la lista completa con el nombre del servidor y las operaciones que puedo hacer con cada uno.
```

**Qué observar:**
- Claude debe listar todos los servidores que configuraste.
- Cada servidor expone herramientas específicas (buscar emails, listar canales, consultar tickets, etc.).
- Si falta algún servidor, revisa que el comando `claude mcp add` se ejecutó sin errores.

---

## Ejercicio 2: Puesta al día matutina (multi-herramienta)

**Requisitos:** Al menos Gmail y Slack configurados. Jira opcional.

**Contexto:** Es lunes por la mañana. En lugar de abrir tres aplicaciones y revisar cada una manualmente, le pides al agente que lo haga por ti.

```text
Necesito ponerme al día con mi semana. Por favor:
1. Revisa mi Gmail y dime los 5 emails más recientes no leídos, con remitente y asunto.
2. Mira en Slack si tengo menciones sin leer en los últimos 3 días.
3. Consulta mis tickets asignados en Jira que estén en estado "En progreso" o "Por hacer".
Dame un resumen ejecutivo con todo junto, priorizando lo que necesita mi atención inmediata.
```

**Qué observar:**
- Claude consultará cada servicio por separado y luego sintetizará.
- El resumen debe priorizar por urgencia, no por orden de llegada.
- Fíjate en cuánto tiempo te ahorra respecto a abrir cada app manualmente.

---

## Ejercicio 3: Informe semanal de proyecto (cruce de datos)

**Requisitos:** Jira, Gmail y Google Drive configurados. Adapta "proyecto Gamma" al nombre de tu proyecto real.

**Contexto:** Es viernes y necesitas el informe semanal. Normalmente dedicarías 45 minutos a recopilar información de tres sitios distintos. Con las herramientas conectadas, le pides al agente que lo haga.

```text
Es viernes y necesito el informe semanal del proyecto Gamma. Por favor:

1. Ve a Jira y consulta el sprint activo del proyecto GAMMA. Dame los tickets completados
   esta semana, los que están en progreso y los bloqueados.
2. Busca en Gmail los emails del cliente (dominio @clientegamma.com) de esta semana
   y extrae las peticiones o decisiones mencionadas.
3. Busca en Google Drive el documento "Decisiones Gamma 2025" y lee las entradas
   de esta semana.
4. Con todo eso, redáctame el informe semanal de estado con esta estructura:
   - Resumen ejecutivo (3 líneas)
   - Progreso del sprint (tickets completados / en progreso / bloqueados)
   - Comunicaciones con el cliente (resumen)
   - Decisiones de la semana
   - Riesgos identificados
   - Plan para la próxima semana
```

**Qué observar:**
- El agente consulta tres fuentes distintas y genera un documento unificado.
- La estructura del informe es tuya; el agente rellena el contenido.
- Revisa siempre el resultado: el agente puede omitir contexto que solo tú conoces.

---

## Ejercicio 4: Preparar una reunión (briefing en 5 minutos)

**Requisitos:** Gmail, Jira y Slack configurados.

**Contexto:** Tienes una reunión en 30 minutos y no has tenido tiempo de prepararte. En lugar de repasar emails, tickets y mensajes a mano, delegas la recopilación.

```text
En 30 minutos tengo reunión con el equipo de ClienteX. Ayúdame a prepararme:

1. Busca en Gmail los últimos 10 emails intercambiados con @clientex.com
   y dame un resumen de los temas tratados.
2. Revisa en Jira los tickets del proyecto CLX que hemos cerrado este mes
   y los que están abiertos.
3. Busca en Slack el canal #clientex y dame las últimas conversaciones
   relevantes de la semana.
4. Con todo eso, prepárame un documento de briefing para la reunión con:
   - Contexto de la relación (temas recientes)
   - Estado del proyecto (lo entregado y lo pendiente)
   - Puntos abiertos que probablemente el cliente mencionará
   - Preguntas que debería hacer yo
```

**Qué observar:**
- El briefing cruza información de tres fuentes que normalmente revisarías por separado.
- Las "preguntas que debería hacer" son especialmente útiles: el agente detecta huecos de información.
- Usa este briefing como punto de partida, no como sustituto de tu preparación.

---

## Ejercicio 5: Auditoría de compromisos (detective de promesas)

**Requisitos:** Gmail, Slack y Jira configurados. Este ejercicio es especialmente útil para gestores de proyecto.

**Contexto:** En cualquier proyecto, los compromisos se dispersan entre emails, mensajes de Slack y tickets. Las tareas que no llegan a un ticket son las que más riesgo tienen de olvidarse. Este prompt pide al agente que cruce fuentes y detecte promesas sin seguimiento.

```text
Necesito una auditoría de compromisos del proyecto Delta de las últimas 2 semanas.
Por favor:

1. Busca en Gmail los emails del equipo del proyecto Delta donde alguien se haya
   comprometido a hacer algo (busca expresiones como "me encargo", "lo tengo",
   "para el viernes", "lo hago yo", "queda de mi parte").
2. Busca en Slack el canal #proyecto-delta mensajes donde alguien haya asumido
   una tarea o dado una fecha de entrega.
3. Consulta en Jira los tickets del proyecto DELTA que se crearon o actualizaron
   en las últimas 2 semanas.
4. Cruza toda la información y dame una tabla con:
   - Persona | Compromiso | Fuente (email/Slack/Jira) | Fecha prometida | Estado
   Identifica especialmente los compromisos que no tienen reflejo en un ticket
   de Jira (son los que más riesgo tienen de caerse).
```

**Qué observar:**
- Este es un caso donde el valor no está en cada fuente individual, sino en el cruce.
- Los compromisos sin ticket son los hallazgos más valiosos.
- El agente puede equivocarse al interpretar intenciones ("lo miro" no siempre es un compromiso). Revisa la tabla con criterio.

---

## Ejercicio 6: Cierre de semana (viernes a las 17:00)

**Requisitos:** Gmail, Jira y Slack configurados.

**Contexto:** Es viernes por la tarde. Quieres irte al fin de semana sabiendo que no se te queda nada importante sin atender.

```text
Es viernes a las 17:00. Prepárame un cierre de semana completo:
1. Jira: tickets que cerré esta semana y los que quedan abiertos para la próxima.
2. Gmail: emails que recibí y no respondí (para no dejar cosas pendientes el fin de semana).
3. Slack: hilos en los que me mencionaron y no respondí.
4. Dame una lista priorizada de las 3 cosas más importantes para el lunes.
```

**Qué observar:**
- La lista de emails sin responder es un chequeo muy práctico para evitar olvidos.
- Las "3 cosas para el lunes" te permiten empezar la semana siguiente con foco.
- Este ejercicio funciona mejor si lo conviertes en rutina semanal.

---

## Preguntas de reflexión

Después de completar los ejercicios, considera:

1. **Valor del cruce:** ¿En cuál de los ejercicios el cruce de fuentes te aportó información que no habrías obtenido revisando cada herramienta por separado?
2. **Confianza y verificación:** ¿En algún momento el agente interpretó mal un email o un mensaje de Slack? ¿Cómo lo detectaste?
3. **Privacidad:** El agente accede a tus emails, mensajes y tickets. ¿Qué política de uso establecerías en un equipo para que esto sea aceptable?
4. **Automatización progresiva:** ¿Cuál de estos flujos convertirías en una rutina diaria o semanal? ¿Qué ajustarías en el prompt para que funcione sin supervisión?
