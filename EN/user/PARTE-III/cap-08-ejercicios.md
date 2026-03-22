# Capítulo 8 — MCP: el puente entre Claude y tus herramientas

Ejercicios prácticos para conectar Claude con tu sistema de archivos local mediante MCP (Model Context Protocol). El objetivo es que experimentes de primera mano cómo un agente accede a herramientas externas.

---

## Ejercicio 1: Instalar y configurar tu primer servidor MCP

**Requisitos:**
- Node.js 18+ instalado ([nodejs.org](https://nodejs.org))
- Claude Desktop instalado, o Claude Code en terminal
- Una carpeta de pruebas con 3-5 archivos variados (un .txt, un .md, un .csv, etc.)

### Paso A — Crear la carpeta de pruebas

Crea una carpeta dedicada para este ejercicio. No uses tu escritorio ni carpetas con información sensible: el servidor MCP tendrá acceso de lectura y escritura a esta carpeta.

Ejemplo en Windows:
```
C:\Users\TU_USUARIO\Documents\MCP-Test
```

Ejemplo en macOS/Linux:
```
/Users/TU_USUARIO/Documents/MCP-Test
```

Crea dentro 3 archivos de ejemplo:
- `notas-proyecto.txt` — unas líneas sobre un proyecto ficticio
- `tareas-semana.md` — una lista de tareas en Markdown
- `contactos.csv` — tres o cuatro filas con nombre, email y teléfono inventados

### Paso B — Configurar el servidor filesystem en Claude Desktop

Abre el archivo de configuración de Claude Desktop:
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

Si el archivo no existe, créalo. Añade esta configuración:

**Windows:**
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "C:\\Users\\TU_USUARIO\\Documents\\MCP-Test"
      ]
    }
  }
}
```

**macOS/Linux:**
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/TU_USUARIO/Documents/MCP-Test"
      ]
    }
  }
}
```

> **Importante:** Sustituye `TU_USUARIO` por tu nombre de usuario real. La ruta debe apuntar exactamente a la carpeta que creaste en el Paso A.

Reinicia Claude Desktop después de guardar el archivo.

### Paso B (alternativa) — Configurar en Claude Code (terminal)

Si prefieres usar Claude Code desde la terminal, el comando es más directo:

```bash
claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem /ruta/a/tu/carpeta
```

Sustituye `/ruta/a/tu/carpeta` por la ruta real. En Windows usa la ruta con barras normales o entre comillas.

---

## Ejercicio 2: Verificar que el puente funciona

**Requisitos:** Ejercicio 1 completado. Claude Desktop o Claude Code con el servidor filesystem activo.

### Paso A — Listar archivos

Abre Claude y escribe:

```text
¿Qué archivos tengo en mi carpeta de pruebas? Dame un listado con el nombre y el tamaño de cada uno.
```

**Qué observar:**
- Claude debería pedir permiso para usar la herramienta `list_directory` (en Claude Desktop aparece un botón de aprobación).
- El resultado debe mostrar los 3 archivos que creaste, con sus tamaños reales.
- Si Claude responde "no tengo acceso a tu sistema de archivos", la configuración MCP no se cargó correctamente. Revisa la ruta y reinicia.

### Paso B — Leer y resumir contenido

```text
Lee todos los archivos de mi carpeta de pruebas y hazme un resumen ejecutivo de lo que contienen.
```

**Qué observar:**
- Claude usará la herramienta `read_file` varias veces (una por archivo).
- El resumen debe reflejar el contenido real de tus archivos, no información inventada.
- Fíjate en cuántas llamadas a herramientas hace: una por archivo, no una sola para todo.

### Paso C — Crear un archivo nuevo

```text
Crea un nuevo archivo llamado "resumen-semanal.md" en mi carpeta de pruebas con un resumen de los tres archivos que has leído.
```

**Qué observar:**
- Claude pedirá permiso para usar `write_file`.
- Después de ejecutar, ve a tu carpeta y comprueba que el archivo existe y tiene contenido coherente.
- Este es el momento clave: el agente no solo lee, también actúa sobre tu entorno real.

---

## Ejercicio 3: Entender los límites del puente

**Requisitos:** Ejercicio 2 completado.

### Paso A — Intentar salir de la carpeta autorizada

```text
Lee el archivo C:\Windows\System32\drivers\etc\hosts
```

(En macOS/Linux: `Lee el archivo /etc/hosts`)

**Qué observar:**
- El servidor filesystem debe rechazar la petición. Solo tiene acceso a la carpeta que configuraste.
- Si Claude dice que no puede acceder, el sandboxing funciona correctamente.
- Si pudiera leer ese archivo, tendrías un problema de seguridad en la configuración.

### Paso B — Reflexión guiada

Responde estas preguntas sin ayuda de Claude:

1. ¿Qué pasaría si configuras el servidor MCP con acceso a `C:\` o `/` (la raíz del sistema)?
2. ¿Por qué el protocolo MCP pide confirmación antes de cada acción?
3. Si conectaras un servidor MCP a tu base de datos de producción, ¿qué controles pondrías?

---

## Ejercicio 4: Operaciones encadenadas

**Requisitos:** Ejercicio 2 completado. Añade 2-3 archivos más a tu carpeta de pruebas para tener variedad.

### Paso A — Análisis y reorganización

```text
Analiza todos los archivos en mi carpeta de pruebas. Para cada uno, dime:
- Nombre actual
- Tipo de contenido (notas, datos, lista, etc.)
- Un nombre más descriptivo siguiendo el formato: YYYY-MM-DD_tipo_descripcion.ext

No renombres nada todavía. Solo muéstrame la tabla con los cambios propuestos.
```

### Paso B — Ejecutar los cambios

Si la tabla te parece correcta:

```text
Aplica los cambios de nombre que propusiste. Después, crea un archivo "registro-cambios.md"
con la tabla de nombres anteriores y nuevos, y la fecha de hoy.
```

**Qué observar:**
- Claude encadena múltiples operaciones: leer, analizar, renombrar, crear.
- Cada operación es una llamada independiente al servidor MCP.
- El archivo de registro te deja una traza auditable de lo que hizo el agente.

---

## Preguntas de reflexión

Después de completar los ejercicios, considera:

1. **Confianza incremental:** ¿Te resultó natural aprobar cada acción, o preferirías que el agente actuara sin pedir permiso? ¿En qué casos?
2. **Alcance mínimo:** El servidor filesystem solo accede a una carpeta. ¿Qué otros servidores MCP te serían útiles en tu trabajo diario?
3. **Del archivo al sistema:** Si MCP puede conectar con archivos, bases de datos, APIs y servicios web, ¿qué proceso repetitivo de tu trabajo podrías automatizar con un puente MCP?
