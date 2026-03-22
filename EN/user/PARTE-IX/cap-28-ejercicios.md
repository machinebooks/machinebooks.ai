# Capitulo 28 — Tu segundo cerebro operativo

Ejercicios practicos para configurar Claude Code como tu asistente operativo diario. Vas a crear tu archivo de contexto personal, conectar herramientas via MCP, definir comandos personalizados para tus tareas recurrentes y establecer una rutina diaria asistida por IA.

---

## Fase 1: Tu archivo CLAUDE.md personal

El archivo `CLAUDE.md` es la memoria persistente de Claude Code. Cada vez que inicias una sesion en una carpeta que contiene este archivo, Claude lo lee automaticamente y adapta su comportamiento.

### Paso A — CLAUDE.md del proyecto (en cada carpeta de trabajo)

Crea un archivo `CLAUDE.md` en la raiz de tu carpeta de trabajo principal:

```markdown
# CLAUDE.md — Mi entorno de trabajo

## Sobre mi
- Nombre: [Tu nombre]
- Rol: [Tu puesto, ej: Responsable de operaciones, Analista de datos, etc.]
- Empresa: [Sector, tamano, contexto relevante]
- Herramientas habituales: [Excel, SAP, Salesforce, Jira, etc.]

## Preferencias de comunicacion
- Respuestas directas, sin rodeos
- Si no sabes algo, dilo en lugar de inventar
- Cuando me des opciones, recomienda una y explica por que
- Formato preferido para informes: Markdown con tablas
- Idioma: espanol de Espana (no latinoamericano)

## Contexto de mi trabajo
- [Describe brevemente a que te dedicas en el dia a dia]
- [Que tipo de tareas te gustaria automatizar]
- [Que datos manejas habitualmente]

## Reglas de seguridad
- NUNCA acceder a carpetas marcadas como confidencial/
- NUNCA incluir datos personales en las respuestas
- Antes de modificar archivos, mostrar que vas a hacer y esperar confirmacion
- Crear log de operaciones en cada sesion

## Proyectos activos
- [Proyecto 1]: [descripcion breve, estado, carpeta]
- [Proyecto 2]: [descripcion breve, estado, carpeta]
- [Proyecto 3]: [descripcion breve, estado, carpeta]
```

### Paso B — CLAUDE.md global (aplica a todas las carpetas)

Claude Code tambien admite un archivo de configuracion global en tu directorio home. Este se aplica en *todas* las sesiones, independientemente de la carpeta:

Ubicacion:
- **Windows:** `C:\Users\TU_USUARIO\.claude\CLAUDE.md`
- **macOS/Linux:** `~/.claude/CLAUDE.md`

```markdown
# Configuracion global de Claude Code

## Preferencias generales
- Siempre responder en espanol
- Usar formato 24h para horas (14:30, no 2:30 PM)
- Usar formato europeo para fechas (25/03/2026, no 03/25/2026)
- Separador de miles: punto (1.000), separador decimal: coma (3,50)
- Moneda por defecto: EUR

## Seguridad global
- Nunca ejecutar comandos con sudo sin confirmacion explicita
- Nunca enviar datos a URLs externas
- Nunca modificar archivos de sistema operativo
- Registrar todas las operaciones que modifiquen archivos

## Estilo de codigo
- Python: seguir PEP 8, comentarios en espanol
- Nombres de variables: en espanol cuando sea codigo interno
- Nombres de funciones: en ingles (convencion de la industria)
```

**Tarea:** Crea ambos archivos adaptados a tu situacion real. No copies las plantillas tal cual — personaliza cada campo con tu informacion.

---

## Fase 2: Conexiones MCP

MCP (Model Context Protocol) permite que Claude Code se conecte con herramientas externas: tu sistema de archivos, tu correo, tu calendario, etc.

### Paso A — Configurar las conexiones

Edita (o crea) el archivo de configuracion de Claude Code:

- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Claude Code (terminal):** `~/.claude/mcp.json`

Configuracion recomendada con tres servidores MCP:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/TU_USUARIO/Documents/trabajo"
      ]
    },
    "gmail": {
      "command": "npx",
      "args": [
        "-y",
        "@anthropic/mcp-server-gmail"
      ],
      "env": {
        "GMAIL_CREDENTIALS_PATH": "/Users/TU_USUARIO/.config/gmail/credentials.json",
        "GMAIL_TOKEN_PATH": "/Users/TU_USUARIO/.config/gmail/token.json"
      }
    },
    "google-calendar": {
      "command": "npx",
      "args": [
        "-y",
        "@anthropic/mcp-server-google-calendar"
      ],
      "env": {
        "GOOGLE_CREDENTIALS_PATH": "/Users/TU_USUARIO/.config/google/credentials.json",
        "GOOGLE_TOKEN_PATH": "/Users/TU_USUARIO/.config/google/token.json"
      }
    }
  }
}
```

> **Importante:** Sustituye `TU_USUARIO` por tu nombre de usuario real. Las rutas deben apuntar a las carpetas correctas en tu sistema.

### Paso B — Verificar las conexiones

Reinicia Claude Code (o Claude Desktop) y verifica que las conexiones funcionan:

```
Muestra las herramientas MCP que tienes disponibles.
Para cada una, indica:
- Nombre del servidor
- Estado (conectado/desconectado)
- Operaciones disponibles
```

Si alguna conexion falla, los errores mas comunes son:
- **Node.js no instalado:** instala Node.js 18+ desde [nodejs.org](https://nodejs.org)
- **Ruta incorrecta:** verifica que la ruta del filesystem apunta a una carpeta existente
- **Credenciales no configuradas:** para Gmail y Calendar necesitas credenciales de API de Google

### Paso C — Probar cada conexion

```
PRUEBA FILESYSTEM:
Lista los archivos en mi carpeta de trabajo.

PRUEBA GMAIL (si esta configurado):
Muestra los 5 ultimos emails recibidos. Solo asunto, remitente y fecha.
NO muestres el cuerpo del email.

PRUEBA CALENDAR (si esta configurado):
Muestra mis eventos de hoy y manana. Solo titulo, hora y duracion.
```

> **Nota:** Si no quieres configurar Gmail y Calendar ahora, empieza solo con filesystem. Podras anadir los demas mas adelante sin reconfigurar nada.

---

## Fase 3: Comandos personalizados

Los comandos personalizados son la funcionalidad mas potente para tu rutina diaria. Cada comando es un archivo Markdown en `.claude/commands/` que define un prompt reutilizable.

### Paso A — Crear la estructura de comandos

```
mkdir -p .claude/commands
```

### Comando 1: procesar-emails.md

Crea el archivo `.claude/commands/procesar-emails.md`:

```markdown
# Procesar emails pendientes

Lee mis emails no leidos de las ultimas 24 horas y genera un resumen ejecutivo.

## Proceso

1. Obtener la lista de emails no leidos (ultimas 24 horas)
2. Para cada email, extraer:
   - Remitente
   - Asunto
   - Resumen del contenido (maximo 2 lineas)
   - Accion requerida: "Responder", "Archivar", "Leer con calma", "Delegable"
   - Urgencia: Alta / Media / Baja

3. Clasificar los emails en estas categorias:
   - **Requieren accion inmediata** (respuesta necesaria hoy)
   - **Informativos** (leer cuando haya tiempo)
   - **Delegables** (puede gestionarlos otra persona)
   - **Descartables** (newsletters, notificaciones automaticas)

## Formato de salida

```
## Bandeja de entrada — [FECHA]

### Accion inmediata (X emails)
| # | Remitente | Asunto | Accion | Urgencia |
|---|-----------|--------|--------|----------|

### Informativos (X emails)
| # | Remitente | Asunto | Resumen |
|---|-----------|--------|---------|

### Delegables (X emails)
| # | Remitente | Asunto | Sugerencia de destinatario |
|---|-----------|--------|---------------------------|

### Descartables (X emails)
- [lista simple de asuntos]

**Total:** X emails procesados
**Tiempo estimado para gestionar acciones inmediatas:** X minutos
```

## Reglas
- NO mostrar el cuerpo completo de ningun email
- NO mostrar direcciones de email completas (solo el nombre del remitente)
- Si un email parece contener datos sensibles (contratos, facturas, datos personales), indicar "CONTIENE DATOS SENSIBLES - revisar manualmente"
- Si hay mas de 50 emails no leidos, procesar solo los 30 mas recientes y avisar
```

### Comando 2: informe-semanal.md

Crea el archivo `.claude/commands/informe-semanal.md`:

```markdown
# Generar informe semanal

Genera un informe de la semana basandose en los archivos de mi carpeta de trabajo.

## Proceso

1. Revisar los archivos modificados en los ultimos 7 dias en la carpeta de trabajo
2. Revisar el log de operaciones de la semana (si existe operaciones-log.md)
3. Revisar los informes generados esta semana en la carpeta informes/

## Formato de salida

```
# Informe semanal — Semana del [LUNES] al [VIERNES]

## Resumen ejecutivo
[3-5 lineas con lo mas importante de la semana]

## Tareas completadas
- [Lista de tareas basandose en archivos creados/modificados]

## Documentos generados
| Documento | Fecha | Tipo | Estado |
|-----------|-------|------|--------|

## Datos procesados
| Dataset | Registros | Resultado | Ubicacion del informe |
|---------|-----------|-----------|----------------------|

## Pendientes para la proxima semana
- [Basandose en archivos en estado "borrador" o carpetas con trabajo incompleto]

## Metricas de productividad
- Archivos creados esta semana: X
- Archivos modificados: X
- Informes generados: X
- Sesiones de Claude Code: X (si hay registro)
```

## Reglas
- Basarse SOLO en evidencia de archivos. No inventar tareas ni resultados.
- Si no hay suficientes datos para una seccion, indicar "Sin datos suficientes" en lugar de rellenar.
- Guardar el informe en informes/semanal-[FECHA].md
```

### Comando 3: preparar-reunion.md

Crea el archivo `.claude/commands/preparar-reunion.md`:

```markdown
# Preparar reunion

Genera un documento de preparacion para una reunion especifica.

## Argumento requerido
$ARGUMENTS — Tema o nombre de la reunion (ej: "revision trimestral con cliente", "seguimiento proyecto X")

## Proceso

1. Buscar en la carpeta de trabajo archivos relacionados con el tema: $ARGUMENTS
2. Revisar emails recientes sobre el tema (si hay acceso a email)
3. Revisar eventos del calendario relacionados (si hay acceso a calendario)

## Formato de salida

```
# Preparacion de reunion: $ARGUMENTS
**Fecha de preparacion:** [HOY]

## Contexto
[Resumen de la situacion actual basandose en archivos encontrados]

## Puntos a tratar
1. [Basado en documentos pendientes, problemas abiertos, etc.]
2. [Basado en comunicaciones recientes]
3. [Basado en compromisos anteriores, si hay registro]

## Datos de apoyo
[Tablas, graficos o metricas relevantes extraidos de los archivos del proyecto]

## Preguntas pendientes
- [Cuestiones que necesitan respuesta en la reunion]

## Documentos relevantes
| Archivo | Ultima modificacion | Relevancia |
|---------|--------------------|-----------|

## Notas para el seguimiento
[Template vacio para rellenar durante la reunion]
- Acuerdos:
- Responsables:
- Proximos pasos:
- Fecha siguiente reunion:
```

## Reglas
- Si no encuentras archivos relacionados con "$ARGUMENTS", indicalo claramente
- No inventar contexto ni datos. Solo usar lo que encuentres en archivos.
- El documento debe ser util como guia impresa para llevar a la reunion
```

### Comando 4: analizar-datos.md

Crea el archivo `.claude/commands/analizar-datos.md`:

```markdown
# Analizar datos

Analiza un archivo de datos y genera un informe estadistico.

## Argumento requerido
$ARGUMENTS — Ruta al archivo de datos (CSV, Excel, JSON) que quieres analizar

## Proceso

1. Leer el archivo: $ARGUMENTS
2. Verificar el contenido antes de procesar:
   - Numero de filas y columnas
   - Tipos de datos por columna
   - Valores nulos o faltantes
   - Mostrar las 5 primeras filas como muestra
3. ESPERAR confirmacion del usuario antes de continuar
4. Generar el analisis completo

## Formato de salida

```
# Analisis de datos: [NOMBRE_ARCHIVO]
**Fecha:** [HOY]
**Filas:** X | **Columnas:** X | **Tamano:** X KB

## Vista previa
[Tabla con las 5 primeras filas]

## Perfil de datos
| Columna | Tipo | No nulos | Nulos | Unicos | Ejemplo |
|---------|------|----------|-------|--------|---------|

## Estadisticas numericas
| Columna | Media | Mediana | Min | Max | Desv. tipica |
|---------|-------|---------|-----|-----|-------------|

## Estadisticas categoricas
| Columna | Valores unicos | Top 3 valores | Frecuencia |
|---------|---------------|---------------|------------|

## Distribuciones destacadas
[Descripcion de patrones, sesgos o concentraciones notables]

## Anomalias detectadas
- [Valores atipicos]
- [Datos faltantes significativos]
- [Inconsistencias entre columnas]

## Recomendaciones
- [Limpieza de datos necesaria antes de usar para analisis avanzado]
- [Columnas que podrian eliminarse por redundancia]
- [Sugerencias de analisis adicionales]
```

## Reglas de privacidad
- Si el archivo contiene columnas que parecen datos personales (nombre, DNI, email, telefono), AVISAR antes de procesar
- Sugerir anonimizacion si se detectan datos sensibles
- NO mostrar filas individuales con datos personales en el informe
```

### Comando 5: estado-proyectos.md

Crea el archivo `.claude/commands/estado-proyectos.md`:

```markdown
# Estado de proyectos

Genera un panel de estado de todos los proyectos activos basandose en la estructura de carpetas y archivos recientes.

## Proceso

1. Listar las subcarpetas de la carpeta de trabajo (cada una es un proyecto)
2. Para cada proyecto, analizar:
   - Fecha del ultimo archivo modificado (actividad reciente)
   - Numero de archivos totales
   - Archivos modificados en los ultimos 7 dias
   - Presencia de archivos "TODO", "PENDIENTE" o similar
   - Presencia de archivos de informe o entregables

## Formato de salida

```
# Panel de proyectos — [FECHA]

## Vista general
| Proyecto | Ultima actividad | Archivos | Modificados (7d) | Estado |
|----------|-----------------|----------|------------------|--------|

Estados posibles:
- 🟢 Activo — archivos modificados en los ultimos 7 dias
- 🟡 Pausado — ultima modificacion hace 7-30 dias
- 🔴 Inactivo — sin cambios en mas de 30 dias
- 📋 Pendiente — tiene archivos TODO o PENDIENTE

## Detalle por proyecto

### [Nombre del proyecto]
- **Ultima actividad:** [fecha]
- **Archivos recientes:** [lista de los 5 mas recientes]
- **Pendientes detectados:** [contenido de TODO/PENDIENTE si existe]
- **Proxima accion sugerida:** [basada en los pendientes]

[Repetir para cada proyecto]

## Resumen
- Proyectos activos: X
- Proyectos pausados: X
- Proyectos inactivos: X
- Acciones pendientes totales: X
```

## Reglas
- Basarse SOLO en la estructura de archivos. No inventar estados ni progreso.
- Si una carpeta esta vacia o solo tiene un README, marcarla como "Sin iniciar"
- No acceder a carpetas marcadas como confidencial/ o privado/
```

### Comando 6: cierre-dia.md

Crea el archivo `.claude/commands/cierre-dia.md`:

```markdown
# Cierre del dia

Genera un resumen de la jornada y prepara la agenda del dia siguiente.

## Proceso

1. Revisar archivos modificados hoy en la carpeta de trabajo
2. Revisar el log de operaciones del dia (operaciones-log.md)
3. Revisar emails procesados hoy (si hay acceso)
4. Revisar eventos de manana en el calendario (si hay acceso)

## Formato de salida

```
# Cierre del dia — [FECHA]

## Lo que se hizo hoy
- [Lista de tareas completadas basandose en archivos creados/modificados]

## Archivos generados hoy
| Archivo | Tipo | Ubicacion |
|---------|------|-----------|

## Temas pendientes para manana
- [Basandose en tareas no completadas, emails sin responder, etc.]

## Agenda de manana
| Hora | Evento | Preparacion necesaria |
|------|--------|----------------------|
[Basado en calendario, si disponible]

## Notas rapidas
[Espacio para que el usuario dicte notas de voz o escriba recordatorios]
-
-
-

## Estado de animo productivo
Basandome en la actividad de hoy:
- **Volumen de trabajo:** Alto / Normal / Bajo
- **Temas cerrados vs abiertos:** X cerrados, X nuevos abiertos
- **Sugerencia:** [Una recomendacion concreta para organizar manana]
```

## Reglas
- NO inventar tareas ni resultados. Solo reportar lo que hay evidencia en archivos.
- Si no hay datos de calendario o email, omitir esas secciones (no dejar secciones vacias con "N/A")
- Guardar el cierre en informes/cierre-[FECHA].md
- Si ya existe un cierre de hoy, preguntar si se quiere sobrescribir o crear version 2
```

---

## Fase 4: Rutina diaria

Ahora que tienes los comandos configurados, establece una rutina diaria con Claude Code.

### Rutina de manana (10-15 minutos)

Al empezar tu jornada, abre Claude Code en tu carpeta de trabajo y ejecuta:

**Comando 1 — Procesar emails:**
```
/procesar-emails
```

Revisa el resumen. Responde los emails urgentes (fuera de Claude). Archiva los descartables.

**Comando 2 — Estado de proyectos:**
```
/estado-proyectos
```

Revisa que proyectos necesitan atencion hoy. Prioriza basandote en urgencia y compromisos.

### Rutina de cierre (5-10 minutos)

Al final de tu jornada:

**Comando 3 — Cierre del dia:**
```
/cierre-dia
```

Revisa el resumen. Anade notas que no esten en los archivos. Confirma la agenda de manana.

### Rutina semanal (viernes, 15-20 minutos)

Cada viernes, ademas del cierre diario:

```
/informe-semanal
```

Usa el informe para tu reunion de seguimiento o para reportar a tu responsable.

> **Consejo:** La rutina funciona mejor si la haces siempre a la misma hora. Despues de 2-3 semanas se convierte en un habito automatico y el tiempo de gestion baja significativamente.

---

## Fase 5: Cuaderno de ajustes

A medida que uses tu segundo cerebro operativo, necesitaras ajustar comandos, reglas y conexiones. Crea un archivo `AJUSTES.md` para registrar que funciona y que no.

### Plantilla de AJUSTES.md

Crea este archivo en la raiz de tu carpeta de trabajo:

```markdown
# AJUSTES.md — Registro de mejoras del sistema

## Formato de entrada
Cada ajuste se registra con:
- **Fecha:** cuando lo detectaste
- **Comando afectado:** cual comando necesita cambio
- **Problema:** que no funciona bien
- **Solucion aplicada:** que cambiaste
- **Resultado:** mejoro, empeoro o sin cambio

---

## Registro de ajustes

### [FECHA] — [Comando/Area]
- **Problema:** [Descripcion]
- **Solucion:** [Que cambiaste]
- **Resultado:** [Mejoro / Empeoro / Sin cambio]

---

## Ideas pendientes de implementar
- [ ] [Idea 1]
- [ ] [Idea 2]
- [ ] [Idea 3]

## Comandos que quiero crear
- [ ] [Comando nuevo 1]: [para que lo usaria]
- [ ] [Comando nuevo 2]: [para que lo usaria]

## Conexiones MCP pendientes
- [ ] [Herramienta]: [por que la necesito]
```

### Como usar AJUSTES.md

1. Cuando un comando no de el resultado esperado, registra el problema
2. Modifica el comando y registra la solucion
3. Despues de usarlo 2-3 veces, evalua si la solucion funciona
4. Cada mes, revisa las ideas pendientes y prioriza cuales implementar

> **Leccion clave:** Tu segundo cerebro operativo no esta terminado nunca. Es un sistema vivo que mejora con cada ajuste. AJUSTES.md es tu diario de mejora continua.

---

## Fase 6: Plan de escalado gradual

No intentes implementar todo de golpe. Sigue este plan de 4 semanas:

### Semana 1 — Fundamentos

**Objetivo:** CLAUDE.md funcional y un comando util

Tareas:
- [ ] Crear CLAUDE.md personal con tu informacion real
- [ ] Crear CLAUDE.md global con tus preferencias generales
- [ ] Configurar MCP filesystem (solo la carpeta de trabajo)
- [ ] Crear el comando `/cierre-dia` y usarlo cada dia de esta semana
- [ ] Crear AJUSTES.md y registrar al menos 2 observaciones

**Criterio de exito:** Al final de la semana, el cierre diario te resulta natural y util.

### Semana 2 — Rutina diaria

**Objetivo:** Rutina de manana y cierre establecida

Tareas:
- [ ] Crear el comando `/procesar-emails` (requiere MCP gmail o adaptarlo a tu flujo)
- [ ] Crear el comando `/estado-proyectos`
- [ ] Establecer la rutina de manana: emails + estado de proyectos
- [ ] Ajustar los comandos de semana 1 segun lo registrado en AJUSTES.md
- [ ] Medir: cuanto tiempo te lleva la rutina de manana? Objetivo: <15 minutos

**Criterio de exito:** La rutina de manana te ahorra tiempo vs hacerlo manualmente.

### Semana 3 — Productividad

**Objetivo:** Automatizar tareas recurrentes especificas de tu trabajo

Tareas:
- [ ] Crear el comando `/analizar-datos` y usarlo con un dataset real
- [ ] Crear el comando `/preparar-reunion` y probarlo con tu proxima reunion
- [ ] Crear el comando `/informe-semanal` y generar el primer informe el viernes
- [ ] Anadir al menos una conexion MCP mas (calendario, u otra herramienta)
- [ ] Revisar AJUSTES.md: que patrones de mejora se repiten?

**Criterio de exito:** Has automatizado al menos 2 tareas que antes hacias manualmente.

### Semana 4 — Consolidacion y expansion

**Objetivo:** Sistema estable y personalizado a tu forma de trabajar

Tareas:
- [ ] Revisar y optimizar todos los comandos segun el registro de AJUSTES.md
- [ ] Crear 1-2 comandos nuevos especificos para tu trabajo (que no esten en esta guia)
- [ ] Documentar tu flujo completo: que haces con Claude y que haces manualmente
- [ ] Evaluar: cuanto tiempo te ahorras a la semana? En que tareas?
- [ ] Planificar el mes siguiente: que mas quieres automatizar?

**Criterio de exito:** Tu sistema funciona sin consultarlo constantemente. Sabes que tareas delegas a Claude y cuales no.

---

## Resumen de aprendizajes

| Fase | Que configuras | Tiempo estimado |
|------|---------------|----------------|
| 1. CLAUDE.md | Tu identidad y preferencias | 30 minutos |
| 2. MCP | Conexiones con herramientas | 30-60 minutos |
| 3. Comandos | 6 automatizaciones recurrentes | 60-90 minutos |
| 4. Rutina | Habito de manana y cierre | 1 semana de practica |
| 5. Ajustes | Mejora continua documentada | 5 minutos por entrada |
| 6. Escalado | Adopcion progresiva | 4 semanas |

**Inversion total:** unas 4-5 horas de configuracion inicial repartidas en un mes. **Retorno estimado:** 30-60 minutos ahorrados por dia laboral una vez que el sistema esta en marcha.

**Principio fundamental:** Tu segundo cerebro operativo no reemplaza tu criterio — amplifica tu capacidad de gestion. Claude procesa, organiza y resume. Tu priorizas, decides y ejecutas lo que importa.
