# Capítulo 23 — Tareas recurrentes: Claude en piloto automático

Ejercicios prácticos para automatizar tareas periódicas con Claude Code, cron y scripts. El objetivo es que configures procesos que se ejecuten solos en los horarios que necesites.

---

## Ejercicio 1: Informe semanal automático todos los lunes a las 9:00

**Prerequisitos:** Claude Code instalado en la máquina donde se ejecutará la tarea. Acceso a los datos semanales en formato CSV. Un directorio de trabajo dedicado.

**Contexto:** Muchos equipos dedican la primera hora del lunes a preparar el informe de la semana anterior. Esta tarea es predecible, repetitiva y siempre sigue la misma estructura. Vamos a delegarla por completo.

### Paso A — Crear la estructura de carpetas

Crea el directorio de trabajo con los datos de ejemplo y las instrucciones para el agente:

```
informe-semanal/
├── datos/
│   ├── ventas-semana.csv        ← columnas: Fecha, Cliente, Producto, Importe, Estado
│   ├── incidencias-semana.csv   ← columnas: Fecha, Tipo, Prioridad, Estado, Descripcion
│   └── tareas-equipo.csv        ← columnas: Responsable, Tarea, Estado, FechaLimite
├── informes/                    ← aquí se guardarán los informes generados
├── CLAUDE.md                    ← instrucciones permanentes para el agente
└── generar-informe.sh           ← script que invoca Claude Code
```

### Paso B — Crear el archivo CLAUDE.md

Este archivo contiene las instrucciones que Claude leerá cada vez que se ejecute. Así no necesitas repetir el prompt:

```markdown
# Instrucciones para el informe semanal

## Datos de entrada
Lee los tres archivos CSV de la carpeta `datos/`:
- ventas-semana.csv
- incidencias-semana.csv
- tareas-equipo.csv

## Estructura del informe
Genera un archivo Markdown en `informes/` con el nombre `informe_YYYY-MM-DD.md`
usando la fecha de hoy. El informe debe contener:

1. RESUMEN EJECUTIVO (5-8 líneas)
   - Total de ventas de la semana
   - Número de incidencias abiertas vs cerradas
   - Porcentaje de tareas completadas

2. VENTAS DE LA SEMANA (tabla)
   - Total por producto
   - Top 5 clientes por importe
   - Operaciones en estado pendiente

3. INCIDENCIAS (tabla + análisis)
   - Incidencias por tipo y prioridad
   - Tiempo medio de resolución si hay datos suficientes
   - Incidencias críticas sin resolver

4. ESTADO DE TAREAS DEL EQUIPO (tabla)
   - Tareas completadas, en curso y retrasadas por responsable
   - Tareas que vencen esta semana

5. CONCLUSIONES Y ALERTAS (3-5 puntos)
   - Tendencias positivas y negativas
   - Riesgos para la próxima semana
   - Acciones recomendadas

## Reglas
- Tono profesional y directo. Si hay datos negativos, exponerlos con claridad.
- No inventar datos que no estén en los CSV.
- Si un archivo CSV está vacío o no existe, indicar "Sin datos disponibles" en esa sección.
```

### Paso C — Crear el script de ejecución

Crea el archivo `generar-informe.sh`:

```bash
#!/bin/bash
# generar-informe.sh — Genera el informe semanal con Claude Code
cd /ruta/a/informe-semanal

claude -p "Lee los archivos CSV de la carpeta datos/ y genera el informe semanal siguiendo las instrucciones de CLAUDE.md. Guarda el resultado en la carpeta informes/ con el nombre informe_$(date +%Y-%m-%d).md" --output-file informes/informe_$(date +%Y-%m-%d).md
```

Dale permisos de ejecución:

```bash
chmod +x generar-informe.sh
```

### Paso D — Programar con cron

Abre el crontab:

```bash
crontab -e
```

Añade esta línea para ejecutar todos los lunes a las 9:00:

```
0 9 * * 1 /ruta/a/informe-semanal/generar-informe.sh >> /ruta/a/informe-semanal/cron.log 2>&1
```

**Qué observar:**
- El archivo `cron.log` registra cada ejecución para diagnosticar problemas.
- Los CSV deben actualizarse antes del lunes (por exportación automática o manualmente el viernes).
- Si necesitas el informe también por email, consulta el prompt de notificación al final de este ejercicio.

### Prompt opcional — Notificación por email

Si tu sistema tiene configurado `sendmail` o `msmtp`, puedes añadir al final del script:

```text
Acabo de generar el informe semanal. Lee el archivo que acabas de crear en informes/
y redacta un email con el asunto "Informe semanal — semana del [fecha]".
El cuerpo del email debe ser un resumen de 10 líneas del informe completo.
Incluye los 3 datos más relevantes y cualquier alerta crítica.
Envíalo a equipo@ejemplo.com usando el comando sendmail disponible en el sistema.
```

---

## Ejercicio 2: Limpieza semanal de archivos todos los viernes a las 18:00

**Prerequisitos:** Claude Code instalado. Una carpeta de descargas y una carpeta temporal que acumulen archivos durante la semana.

**Contexto:** Las carpetas de descargas y temporales crecen sin control. Cada viernes antes de cerrar la semana, este proceso limpia lo innecesario, detecta duplicados y deja un registro de lo que se borró.

### Paso A — Crear el script de limpieza

Crea el archivo `limpieza-semanal.sh`:

```bash
#!/bin/bash
# limpieza-semanal.sh — Limpieza automatizada con Claude Code
FECHA=$(date +%Y-%m-%d)
LOG_DIR="/ruta/a/limpieza/logs"
mkdir -p "$LOG_DIR"

claude -p "$(cat <<'PROMPT'
Realiza la limpieza semanal de archivos siguiendo estos pasos en orden:

FASE 1 — ANÁLISIS DE LA CARPETA DE DESCARGAS
Analiza la carpeta ~/Descargas (o ~/Downloads):
- Lista todos los archivos con su tamaño y fecha de última modificación.
- Identifica archivos con más de 30 días sin modificar.
- Detecta duplicados: archivos con el mismo nombre pero con sufijo (1), (2), copia, etc.
- Detecta archivos temporales: .tmp, .partial, .crdownload, .part.

FASE 2 — LIMPIEZA DE ARCHIVOS TEMPORALES
Busca y elimina en ~/tmp o /tmp (solo archivos del usuario actual):
- Archivos .tmp con más de 7 días de antigüedad.
- Carpetas vacías.
- Archivos de caché que superen los 100 MB.

FASE 3 — DETECCIÓN DE DUPLICADOS
En ~/Descargas, identifica grupos de archivos duplicados:
- Compara por nombre similar (ignorando sufijos numéricos).
- Para cada grupo, conserva el más reciente y marca los demás para borrar.
- IMPORTANTE: NO borres duplicados automáticamente. Genera una lista de candidatos a eliminar.

FASE 4 — INFORME Y EJECUCIÓN
Genera un informe en Markdown con:
- Archivos eliminados (temporales y antiguos): nombre, tamaño, motivo.
- Duplicados detectados: grupos con la recomendación de cuál conservar.
- Espacio total liberado.
- Errores encontrados (archivos protegidos, permisos insuficientes).

Borra solo los archivos de Fase 1 (>30 días) y Fase 2 (temporales).
Los duplicados de Fase 3 solo se listan, no se borran sin confirmación.

Guarda el informe como ~/limpieza/logs/limpieza_FECHA.md
PROMPT
)" >> "$LOG_DIR/limpieza_${FECHA}.log" 2>&1
```

### Paso B — Programar con cron

```
0 18 * * 5 /ruta/a/limpieza-semanal.sh
```

**Qué observar:**
- La Fase 3 es deliberadamente conservadora: detecta duplicados pero no los borra sin revisión.
- El log de cada ejecución se conserva para auditar qué se eliminó y cuándo.
- Adapta las rutas a tu sistema operativo (en macOS: `~/Downloads`, en Linux: `~/Descargas` si usas español).

### Prompt opcional — Notificación por email

```text
La limpieza semanal ha terminado. Lee el informe de limpieza más reciente
en ~/limpieza/logs/ y redacta un email breve con:
- Espacio liberado en total.
- Número de archivos eliminados.
- Si hay duplicados pendientes de revisión manual, indicar cuántos grupos.
Asunto: "Limpieza semanal completada — [fecha]"
Envíalo a admin@ejemplo.com usando sendmail.
```

---

## Ejercicio 3: Copia de seguridad diaria con verificación a las 23:00

**Prerequisitos:** Claude Code instalado. Carpetas de trabajo que necesiten respaldo diario. Espacio suficiente en disco o en una unidad externa.

**Contexto:** Una copia de seguridad que no se verifica es una copia que puede fallar cuando más la necesitas. Este proceso no solo crea el archivo comprimido, sino que verifica su integridad y alerta si algo sale mal.

### Paso A — Crear el script de backup

Crea el archivo `backup-diario.sh`:

```bash
#!/bin/bash
# backup-diario.sh — Backup con verificación usando Claude Code
FECHA=$(date +%Y-%m-%d)
BACKUP_DIR="/ruta/a/backups"
LOG_DIR="/ruta/a/backups/logs"
mkdir -p "$BACKUP_DIR" "$LOG_DIR"

claude -p "$(cat <<PROMPT
Realiza la copia de seguridad diaria siguiendo estos pasos:

FASE 1 — CREAR EL ARCHIVO COMPRIMIDO
Comprime las siguientes carpetas en un único archivo tar.gz:
- ~/Documentos/Proyectos
- ~/Documentos/Finanzas
- ~/Documentos/Contratos

Nombre del archivo: $BACKUP_DIR/backup_${FECHA}.tar.gz

Excluye de la compresión:
- Archivos mayores de 500 MB (probablemente son vídeos o imágenes ISO).
- Carpetas node_modules, .git, __pycache__, .venv.
- Archivos .tmp, .log, .cache.

FASE 2 — VERIFICAR LA INTEGRIDAD
Después de crear el archivo:
1. Comprueba que el archivo tar.gz se puede leer sin errores: tar -tzf archivo.tar.gz > /dev/null
2. Registra el tamaño del archivo comprimido.
3. Compara con el backup del día anterior (si existe): diferencia de tamaño.
4. Si el archivo pesa menos del 50% que el del día anterior, marca como ALERTA.

FASE 3 — ROTACIÓN
Si hay más de 7 archivos de backup en $BACKUP_DIR:
- Elimina los más antiguos, conservando siempre los últimos 7 días.
- Registra qué archivos se eliminaron.

FASE 4 — INFORME
Genera un informe breve en $LOG_DIR/backup_${FECHA}.log con:
- Estado: OK o ERROR
- Tamaño del backup
- Número de archivos incluidos
- Archivos excluidos por tamaño (si los hubo)
- Backups antiguos eliminados (si los hubo)
- Alertas (si las hubo)
PROMPT
)" >> "$LOG_DIR/backup_${FECHA}.log" 2>&1
```

### Paso B — Programar con cron

```
0 23 * * * /ruta/a/backup-diario.sh
```

### Paso C — Añadir alerta en caso de fallo

Para recibir notificación cuando algo falla, añade al final del script:

```bash
# Verificar si el backup se creó correctamente
if [ ! -f "$BACKUP_DIR/backup_${FECHA}.tar.gz" ]; then
    claude -p "El backup diario del $FECHA ha FALLADO. El archivo no se creó. Redacta un email de alerta urgente con asunto 'ALERTA: Backup fallido — $FECHA' explicando que la copia de seguridad no se completó y que se requiere intervención manual. Envíalo a admin@ejemplo.com usando sendmail."
fi
```

### Prompt opcional — Notificación diaria de estado

```text
Lee el log de backup más reciente en /ruta/a/backups/logs/.
Si el estado es OK, envía un email breve con asunto "Backup diario OK — [fecha]"
indicando el tamaño y el número de archivos.
Si el estado es ERROR o hay alguna ALERTA, envía un email con asunto
"ALERTA: Backup diario — [fecha]" describiendo el problema encontrado.
Envíalo a admin@ejemplo.com usando sendmail.
```

---

## Preguntas de reflexión

Después de completar los ejercicios, considera:

1. **Confianza en la automatización:** Los tres ejercicios usan `claude -p` en modo no interactivo. ¿Qué mecanismos de seguridad añadirías antes de ejecutar estos scripts en un servidor de producción?
2. **Escalado:** Si necesitaras ejecutar estas tareas en 10 máquinas distintas, ¿cómo gestionarías la distribución de los scripts y las instrucciones CLAUDE.md?
3. **Límites del agente:** ¿En qué punto una tarea recurrente deja de ser candidata para Claude Code y debería implementarse como un script convencional sin IA?
