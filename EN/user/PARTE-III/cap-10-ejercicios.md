# Capítulo 10 — Construir tu propio conector MCP

Ejercicios prácticos para crear un servidor MCP personalizado en Python. El objetivo es que construyas tu propio puente entre Claude y una API que no tiene servidor MCP oficial.

---

## Ejercicio 1: Preparar el entorno de desarrollo

**Requisitos:**
- Python 3.10 o superior instalado
- Terminal con acceso a `pip`
- Un editor de texto o IDE (VS Code recomendado)

### Paso A — Crear la carpeta del proyecto

Crea una carpeta dedicada para tu servidor MCP:

```bash
mkdir mi-servidor-mcp
cd mi-servidor-mcp
```

### Paso B — Crear el entorno virtual

```bash
python -m venv venv
```

Activar el entorno:
- **Windows:** `venv\Scripts\activate`
- **macOS/Linux:** `source venv/bin/activate`

### Paso C — Crear el archivo de dependencias

Crea un archivo `requirements.txt` con este contenido:

```text
mcp[cli]>=1.0.0
httpx>=0.27.0
```

Instala las dependencias:

```bash
pip install -r requirements.txt
```

### Paso D — Verificar la instalación

```bash
python -c "import mcp; print('MCP versión:', mcp.__version__)"
```

Si ves la versión sin errores, el entorno está listo.

---

## Ejercicio 2: Crear un servidor MCP mínimo

**Requisitos:** Ejercicio 1 completado.

### Paso A — Escribir el servidor

Crea el archivo `servidor.py` con un servidor MCP mínimo que simula un sistema de gestión de clientes. No necesitas una API real: el servidor usa datos ficticios para que puedas probarlo sin dependencias externas.

El servidor debe:
1. Importar `FastMCP` del paquete `mcp`
2. Definir una lista de clientes ficticios (5-6 registros con nombre, email, empresa y estado)
3. Exponer una herramienta `buscar_cliente` que reciba un texto de búsqueda y devuelva los clientes que coincidan por nombre o empresa
4. Exponer una herramienta `listar_clientes_activos` que devuelva solo los clientes con estado "activo"

> **Pista:** Consulta el código del capítulo para ver la estructura exacta de un servidor MCP con `FastMCP`. La clave es el decorador `@mcp.tool()` sobre cada función.

### Paso B — Probar en modo desarrollo

Ejecuta el servidor en modo inspector para verificar que funciona:

```bash
mcp dev servidor.py
```

Esto abre un inspector web donde puedes invocar tus herramientas manualmente y ver las respuestas.

### Paso C — Conectar con Claude Code

Registra tu servidor en Claude Code:

```bash
claude mcp add mi-gestion -- python /ruta/completa/a/servidor.py
```

Sustituye `/ruta/completa/a/servidor.py` por la ruta real al archivo.

---

## Ejercicio 3: Verificar que Claude usa tu servidor

**Requisitos:** Ejercicio 2 completado. Claude Code con el servidor `mi-gestion` registrado.

### Paso A — Descubrir herramientas

Abre Claude Code y pregunta:

```text
¿Qué herramientas MCP tengo disponibles? ¿Hay alguna nueva?
```

**Qué observar:**
- Claude debe listar tus herramientas `buscar_cliente` y `listar_clientes_activos`.
- Si no aparecen, verifica que el servidor arranca sin errores ejecutando `python servidor.py` directamente.

### Paso B — Usar la herramienta con lenguaje natural

```text
Busca al cliente García en el sistema de gestión.
```

**Qué observar:**
- Claude debe invocar `buscar_cliente` con el término "García".
- El resultado debe mostrar los clientes ficticios que coincidan.
- Claude interpreta tu petición en lenguaje natural y la traduce a una llamada a herramienta con los parámetros correctos.

### Paso C — Combinar con otras herramientas

Si tienes Gmail configurado del capítulo anterior:

```text
Busca al cliente García en el sistema de gestión y luego revisa en Gmail
si tenemos emails recientes de ese cliente. Si hay pedidos pendientes
y emails sin responder, avísame.
```

**Qué observar:**
- Claude usa dos servidores MCP distintos en la misma conversación: tu servidor personalizado y el de Gmail.
- El agente cruza datos de ambas fuentes para darte una respuesta integrada.
- Este es el patrón central del capítulo: herramientas heterogéneas que el agente orquesta.

---

## Ejercicio 4: Pedir a Claude que escriba tu servidor MCP

**Requisitos:** Claude Code activo. No necesitas código previo.

**Contexto:** No siempre tienes que escribir el servidor tú mismo. Claude puede generar el código completo si le describes la API a la que quieres conectarte.

### Paso A — Describir la API y pedir el servidor

```text
Necesito que me crees un servidor MCP en Python que se conecte a una API REST
en https://api.interna.miempresa.com/v2. La API usa autenticación Bearer Token.

Quiero estas herramientas:
1. Buscar empleados por nombre o departamento
2. Consultar las vacaciones pendientes de un empleado
3. Listar los proyectos activos

La API tiene estos endpoints:
- GET /empleados?buscar=nombre&departamento=dept
- GET /empleados/{id}/vacaciones
- GET /proyectos?estado=activo

Créame el archivo servidor.py y requirements.txt listos para usar.
```

**Qué observar:**
- Claude genera un servidor MCP completo con las tres herramientas.
- Cada herramienta tiene docstring, tipado de parámetros y manejo de errores.
- El token de autenticación se lee de una variable de entorno (no está hardcodeado).
- Revisa el código generado antes de ejecutarlo. Comprueba que los endpoints coinciden con lo que describiste.

### Paso B — Revisar y adaptar

Antes de usar el servidor generado, verifica:

1. ¿Los nombres de las herramientas son descriptivos?
2. ¿Los parámetros tienen tipos correctos y descripciones claras?
3. ¿Hay manejo de errores para cuando la API no responde?
4. ¿El token se lee de variable de entorno o está hardcodeado?

Si algo no te convence, pide a Claude que lo corrija:

```text
Cambia el nombre de la herramienta "buscar_empleados" a "buscar_persona" y añade
un parámetro opcional "sede" para filtrar por oficina.
```

---

## Ejercicio 5: Depurar problemas comunes

**Requisitos:** Haber intentado los ejercicios anteriores. Este ejercicio es para cuando algo no funciona.

### Problema A — El servidor no aparece en Claude

**Diagnóstico:**

```bash
mcp dev servidor.py
```

Si el inspector web no carga o muestra errores, revisa:
- ¿El archivo `servidor.py` tiene errores de sintaxis? Ejecuta `python servidor.py` directamente.
- ¿Las dependencias están instaladas? Ejecuta `pip install -r requirements.txt` de nuevo.
- ¿Estás en el entorno virtual correcto? Verifica con `which python` (macOS/Linux) o `where python` (Windows).

### Problema B — Claude no usa la herramienta

Si Claude responde sin invocar tu herramienta:
- Verifica que el servidor está registrado: `claude mcp list`
- Comprueba que el nombre de la herramienta tiene sentido. Si se llama `tool_1`, Claude no sabrá cuándo usarla. Renómbrala a algo descriptivo.
- Asegúrate de que la función tiene un docstring claro. Claude usa la descripción para decidir cuándo invocar cada herramienta.

### Problema C — La herramienta devuelve un error

Si Claude invoca la herramienta pero el resultado es un error:
- Revisa los logs del servidor en la terminal donde lo ejecutaste.
- Comprueba que la URL de la API es accesible desde tu máquina.
- Verifica que el token de autenticación es válido.

---

## Preguntas de reflexión

Después de completar los ejercicios, considera:

1. **Tu primer conector:** ¿Qué sistema de tu trabajo diario no tiene servidor MCP oficial y te gustaría conectar? ¿Tiene API REST documentada?
2. **Generación vs. escritura manual:** ¿Fue más rápido pedirle a Claude que generara el servidor o lo habrías escrito más rápido tú? ¿En qué casos prefieres cada enfoque?
3. **Seguridad:** Tu servidor MCP tiene acceso a una API con datos reales. ¿Qué controles añadirías antes de usarlo en producción? Piensa en: permisos de solo lectura, logging de llamadas, límites de uso.
4. **Composición:** Ahora que sabes crear servidores MCP, ¿qué combinación de 3-4 herramientas (oficiales + tuyas) resolverían tu flujo de trabajo más tedioso?
