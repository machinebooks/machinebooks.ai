# Capítulo 19 — Tu terminal potenciada

Ejercicios prácticos con prompts listos para copiar y pegar en Claude Code o Claude Desktop.

---

## Ejercicio 1: Análisis de logs de Nginx (últimos 7 días)

**Prerequisitos:** Acceso a los archivos de log de Nginx (normalmente en `/var/log/nginx/`). Los logs deben estar en formato estándar combinado. Si no tienes logs reales, genera unos de prueba con entradas variadas de los últimos 7 días.

**Contexto:** Cuando un servidor web empieza a dar problemas, lo primero es entender qué está pasando en los logs. Este ejercicio se centra en los errores del rango 500-504, que indican fallos en el lado del servidor.

**Resultado esperado:** Un informe Markdown con tablas de frecuencia, líneas temporales de errores y recomendaciones priorizadas.

```text
Analiza los logs de Nginx en /var/log/nginx/access.log y
/var/log/nginx/error.log de los últimos 7 días.

Céntrate exclusivamente en los errores HTTP del rango 500-504.
Para cada tipo de error necesito:

1. RESUMEN GENERAL
   - Total de peticiones en los 7 días
   - Total de errores 5xx y porcentaje sobre el total
   - Desglose por código: 500, 502, 503, 504

2. DISTRIBUCIÓN TEMPORAL
   - Tabla con errores por día y hora pico de cada día
   - Identifica si hay un patrón (¿siempre a la misma hora?
     ¿un día concreto?)

3. URLs MÁS AFECTADAS
   - Top 15 URLs que generan más errores 5xx
   - Para cada una: código más frecuente, número de ocurrencias,
     última vez que ocurrió

4. IPs DE ORIGEN
   - Top 10 IPs que más errores 5xx reciben
   - ¿Alguna IP concentra un porcentaje anómalo?

5. CORRELACIÓN CON ERROR.LOG
   - Busca en error.log las entradas correspondientes a los
     timestamps de los errores 5xx del access.log
   - Agrupa los mensajes de error por tipo

6. DIAGNÓSTICO Y RECOMENDACIONES
   - Causa probable de cada tipo de error detectado
   - Acciones concretas ordenadas por prioridad

Guarda el informe como informe-nginx-7d.md en el directorio actual.
Si los logs están comprimidos (.gz), descomprímelos primero.
```

---

## Ejercicio 2: Organización de archivos de backup

**Prerequisitos:** Una carpeta con archivos de backup acumulados durante meses. Idealmente `/var/backups/` o una carpeta similar con ficheros `.tar.gz`, `.sql.gz`, `.bak` y similares. Si no tienes una, crea una carpeta de prueba con 50-60 archivos simulados con fechas variadas.

**Contexto:** Las carpetas de backup tienden a crecer sin control. Este ejercicio mueve los archivos de más de 30 días a una subcarpeta de archivo, manteniendo intactos los recientes.

**Resultado esperado:** Los archivos antiguos movidos a `archive/`, un log detallado de las operaciones y un resumen con el espacio liberado.

```text
Organiza la carpeta /var/backups/ siguiendo estas reglas:

1. INVENTARIO INICIAL
   - Lista todos los archivos con tamaño y fecha de modificación
   - Calcula el espacio total ocupado
   - Clasifica por extensión (.tar.gz, .sql.gz, .bak, .zip, otros)

2. CLASIFICACIÓN POR ANTIGÜEDAD
   - Recientes: modificados en los últimos 30 días → no tocar
   - Antiguos: más de 30 días → mover a /var/backups/archive/

3. EJECUCIÓN
   - Crea /var/backups/archive/ si no existe
   - Mueve los archivos antiguos a archive/
   - NO borres nada, solo mueve
   - Mantén la estructura de nombres original

4. REGISTRO DE OPERACIONES
   - Genera un archivo mover-backups.log con cada operación:
     [FECHA] MOVIDO: archivo.tar.gz (tamaño) → archive/
   - Al final del log, incluye un resumen:
     - Archivos movidos: N
     - Espacio movido a archive: X GB
     - Archivos que permanecen: M
     - Espacio activo restante: Y GB

5. INFORME FINAL
   - Guarda como organizacion-backups.md
   - Incluye el estado antes y después
   - Si detectas archivos sospechosos (0 bytes, nombres raros,
     extensiones inesperadas), márcalos aparte

Antes de mover nada, muéstrame el plan y espera confirmación.
```

---

## Ejercicio 3: Auditoría de intentos de login SSH fallidos

**Prerequisitos:** Acceso al archivo `/var/log/auth.log` (Debian/Ubuntu) o `/var/log/secure` (CentOS/RHEL). Necesitas permisos de lectura sobre estos ficheros (normalmente requiere `sudo`).

**Contexto:** Los servidores expuestos a internet reciben miles de intentos de acceso SSH por fuerza bruta. Este ejercicio genera un informe CSV estructurado que permite analizar los patrones de ataque.

**Resultado esperado:** Un archivo CSV con las columnas especificadas, un resumen en Markdown con estadísticas y recomendaciones de seguridad.

```text
Genera un informe de auditoría de intentos de login SSH fallidos
a partir de /var/log/auth.log (o /var/log/secure si estamos en
CentOS/RHEL).

PASO 1: EXTRACCIÓN DE DATOS
Busca todas las líneas que contengan "Failed password" o
"authentication failure" y extrae:
- Fecha y hora del intento
- IP de origen
- Usuario intentado
- Método (password, publickey, etc.)

PASO 2: GENERAR CSV
Crea el archivo ssh-audit.csv con estas columnas:
fecha,hora,ip_origen,usuario,metodo,pais_estimado

Para el país estimado, usa el comando "whois" sobre las IPs
únicas y extrae el campo country. Si no puedes resolver alguna,
pon "desconocido".

PASO 3: ANÁLISIS ESTADÍSTICO
Genera ssh-audit-informe.md con:

1. Resumen ejecutivo
   - Total de intentos fallidos en el periodo
   - Rango de fechas analizado
   - Número de IPs únicas
   - Número de usuarios únicos probados

2. Top 20 IPs atacantes (tabla con IP, país, intentos, primera
   y última vez)

3. Top 20 usuarios probados (tabla con usuario, intentos,
   número de IPs distintas que lo probaron)

4. Distribución temporal (intentos por hora del día y por día
   de la semana)

5. Patrones sospechosos
   - IPs que prueban más de 10 usuarios distintos
   - Usuarios que no existen en el sistema
   - Ráfagas (más de 50 intentos en 5 minutos desde la misma IP)

6. Recomendaciones de seguridad
   - IPs candidatas a bloquear con iptables/fail2ban
   - Usuarios del sistema que deberían revisarse
   - Configuraciones SSH recomendadas
```

---

## Ejercicio 4: Gestión de espacio en disco (/var al 92%)

**Prerequisitos:** Un servidor donde la partición `/var` está cerca de llenarse (o simula la situación creando ficheros grandes temporales). Acceso con permisos de administrador.

**Contexto:** Cuando `/var` supera el 90% de ocupación, los servicios empiezan a fallar: las bases de datos no pueden escribir, los logs se truncan, las colas se bloquean. Este ejercicio es un procedimiento de emergencia controlado.

**Resultado esperado:** Un diagnóstico completo del uso de disco, un plan de limpieza con estimaciones de espacio recuperable, y un script de mantenimiento preventivo.

```text
La partición /var está al 92% de capacidad. Necesito un diagnóstico
completo y un plan de acción.

FASE 1: DIAGNÓSTICO
- Ejecuta df -h para ver el estado general de las particiones
- Ejecuta du -sh /var/*/ para identificar los subdirectorios
  más grandes
- Para los 5 directorios más grandes dentro de /var, profundiza
  un nivel más con du -sh
- Busca archivos de más de 100 MB en /var: find /var -size +100M
- Identifica logs rotados antiguos que puedan borrarse
- Revisa /var/tmp y /var/cache

FASE 2: PLAN DE ACCIÓN (NO EJECUTAR TODAVÍA)
Genera una tabla con estas columnas:
| Acción | Ruta | Espacio estimado | Riesgo | Prioridad |

Clasifica las acciones en:
- Sin riesgo: logs rotados antiguos, caches, archivos temporales
- Riesgo bajo: paquetes descargados (apt/yum cache)
- Riesgo medio: logs activos que pueden truncarse
- No tocar: datos de aplicación, bases de datos

FASE 3: SCRIPT DE MANTENIMIENTO
Genera un script limpieza-var.sh que:
- Limpia logs rotados de más de 7 días
- Vacía /var/tmp de archivos de más de 3 días
- Limpia cache de paquetes (apt clean / yum clean all)
- Registra cada acción en un log
- Muestra el espacio antes y después
- Requiere confirmación antes de borrar

FASE 4: CRON PREVENTIVO
Sugiere una entrada de cron que ejecute un chequeo semanal
y envíe alerta si /var supera el 80%.

Guarda todo en el directorio actual:
- diagnostico-var.md (fases 1 y 2)
- limpieza-var.sh (fase 3)
- cron-alerta-disco.sh (fase 4)
```

---

## Ejercicio 5: Informe semanal de salud del servidor

**Prerequisitos:** Un servidor Linux con acceso a los comandos estándar de monitorización (`uptime`, `free`, `df`, `top`, `ss`, `systemctl`, `journalctl`). No se requiere software de monitorización adicional.

**Contexto:** Muchos equipos pequeños no tienen Grafana ni Datadog. Este ejercicio genera un informe semanal completo usando solo herramientas del sistema, automatizable con cron para que se genere cada lunes a las 7:00.

**Resultado esperado:** Un informe Markdown con 6 secciones, listo para enviar por correo o guardar en un repositorio de documentación.

```text
Genera un informe semanal de salud del servidor con estas 6 secciones.
Usa únicamente comandos del sistema (no instales nada nuevo).

1. ESTADO GENERAL
   - Hostname, IP, sistema operativo, kernel
   - Uptime y última vez que se reinició
   - Carga media (1, 5, 15 minutos)
   - Usuarios conectados actualmente

2. CPU Y MEMORIA
   - Uso de CPU: promedio y picos (si hay datos en /proc)
   - Memoria RAM: total, usada, libre, cache/buffers
   - Swap: uso actual y si se ha usado esta semana
   - Top 5 procesos por consumo de CPU
   - Top 5 procesos por consumo de RAM

3. ALMACENAMIENTO
   - Tabla con todas las particiones: montaje, tamaño, usado,
     disponible, porcentaje
   - Marca en rojo (con **) las que superen el 80%
   - Inodos: uso por partición

4. SERVICIOS CRÍTICOS
   - Estado de: nginx, postgresql, redis, docker
   - Para cada uno: activo/inactivo, uptime, últimos errores
     en journalctl (últimas 24h)
   - Si alguno se reinició esta semana, indicar cuántas veces

5. RED Y CONEXIONES
   - Interfaces de red activas con IP
   - Conexiones establecidas (ss -s)
   - Puertos en escucha (ss -tlnp)
   - Si hay conexiones en estado TIME_WAIT excesivas, indicarlo

6. SEGURIDAD BÁSICA
   - Últimos 5 accesos SSH exitosos
   - Intentos de acceso fallidos en las últimas 24h
   - Actualizaciones de seguridad pendientes
   - Certificados SSL que caduquen en menos de 30 días
     (buscar en /etc/letsencrypt/ o /etc/ssl/)

Guarda el informe como salud-servidor-YYYY-MM-DD.md
(usa la fecha de hoy).
Al final, sugiere un cron para ejecutar esto cada lunes a las 7:00.
```

---

## Ejercicio 6: Análisis de URLs lentas en Apache

**Prerequisitos:** Acceso a los logs de Apache (`/var/log/apache2/access.log` o `/var/log/httpd/access_log`). El log debe estar en formato combinado e incluir el campo `%D` (tiempo de respuesta en microsegundos) o `%T` (en segundos). Si tu formato no incluye tiempos de respuesta, el ejercicio te guía para configurarlo.

**Contexto:** Identificar las URLs más lentas de un servidor web es el primer paso para optimizar el rendimiento. Este ejercicio extrae los datos de latencia directamente de los logs sin necesidad de herramientas APM.

**Resultado esperado:** Un ranking de URLs lentas, análisis de patrones temporales y recomendaciones de optimización priorizadas.

```text
Analiza los logs de Apache para identificar las URLs más lentas.

PASO 0: VERIFICAR FORMATO
Comprueba si el log incluye tiempo de respuesta (%D o %T).
Si no lo incluye, dime qué línea añadir en la configuración
de Apache para habilitarlo y avísame antes de continuar.

Ruta del log: /var/log/apache2/access.log

PASO 1: EXTRACCIÓN
Analiza las últimas 100.000 líneas del log. Extrae:
- URL (sin query string)
- Método HTTP
- Código de respuesta
- Tiempo de respuesta
- Timestamp

PASO 2: RANKING DE LATENCIA
Genera estas tablas:

a) Top 20 URLs más lentas (por tiempo medio de respuesta)
   Columnas: URL, método, tiempo medio, tiempo máximo,
   percentil 95, número de peticiones

b) Top 10 URLs con mayor tiempo acumulado
   (las que más tiempo total de servidor consumen)
   Columnas: URL, peticiones, tiempo medio, tiempo total

c) URLs con latencia inconsistente
   (donde el p95 es más del doble que la media)

PASO 3: ANÁLISIS TEMPORAL
- ¿Las URLs lentas son lentas siempre o solo en ciertos
  horarios?
- ¿Hay correlación entre volumen de tráfico y latencia?

PASO 4: RECOMENDACIONES
Para cada URL del top 10, sugiere la causa probable y la
acción correctiva:
- ¿Consulta SQL lenta?
- ¿Falta de cache?
- ¿Procesamiento pesado en servidor?
- ¿Recurso estático que debería servir CDN/Nginx?

Guarda como analisis-latencia-apache.md
```

---

## Ejercicio 7: Edición de configuración de Nginx

**Prerequisitos:** Un servidor con Nginx instalado y acceso de escritura a su configuración (normalmente `/etc/nginx/nginx.conf`). Antes de empezar, haz una copia de seguridad: `cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup`.

**Contexto:** Tres ajustes frecuentes en Nginx que mejoran rendimiento y seguridad: aumentar `worker_connections`, configurar limitación de tasa (rate limiting) y habilitar compresión gzip. Este ejercicio los aplica paso a paso con validación.

**Resultado esperado:** Configuración de Nginx modificada, validada con `nginx -t` y aplicada. Un documento que explica cada cambio realizado.

```text
Necesito hacer tres ajustes en la configuración de Nginx.
Antes de cada cambio, muestra el estado actual del parámetro.

CAMBIO 1: WORKER CONNECTIONS
- Archivo: /etc/nginx/nginx.conf
- Localiza el bloque events {}
- Cambia worker_connections al valor calculado así:
  (número de CPUs × 1024). Usa nproc para obtener las CPUs
- Si ya tiene un valor adecuado, déjalo y explica por qué

CAMBIO 2: RATE LIMITING
- Añade una zona de limitación de tasa para proteger contra
  abuso:
  limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;
- Aplica la limitación en el bloque server principal:
  limit_req zone=general burst=20 nodelay;
- Configura una respuesta personalizada para código 429

CAMBIO 3: COMPRESIÓN GZIP
- Habilita gzip con estos parámetros:
  gzip on;
  gzip_vary on;
  gzip_proxied any;
  gzip_comp_level 4;
  gzip_min_length 256;
  gzip_types text/plain text/css application/json
    application/javascript text/xml application/xml
    application/xml+rss text/javascript image/svg+xml;

VALIDACIÓN
- Ejecuta nginx -t para verificar la sintaxis
- Si hay errores, corrígelos antes de continuar
- Muestra un diff entre la configuración original y la nueva
- Aplica con systemctl reload nginx
- Confirma que Nginx sigue respondiendo: curl -I http://localhost

DOCUMENTACIÓN
- Guarda como cambios-nginx.md con:
  - Qué se cambió y por qué
  - Valores anteriores y nuevos
  - Cómo revertir cada cambio
```

---

## Ejercicio 8: Gestión de permisos de archivos

**Prerequisitos:** Una aplicación web desplegada en `/var/www/app/` (o crea una estructura de prueba con subcarpetas `public/`, `config/`, `logs/`, `uploads/` y archivos simulados). Acceso con permisos de administrador.

**Contexto:** Los permisos incorrectos son una de las causas más frecuentes de fallos en aplicaciones web y también un vector de ataque habitual. Este ejercicio audita y corrige la estructura de permisos siguiendo las prácticas recomendadas.

**Resultado esperado:** Un informe de auditoría con los problemas encontrados, los permisos corregidos y un script reutilizable para aplicar la misma política en otros despliegues.

```text
Audita y corrige los permisos de la aplicación web en
/var/www/app/

FASE 1: AUDITORÍA ACTUAL
Lista la estructura completa con permisos, propietario y grupo:
find /var/www/app/ -ls

Identifica problemas:
- Archivos con permisos 777 (lectura/escritura/ejecución para todos)
- Archivos propiedad de root que deberían ser del usuario web
- Archivos de configuración legibles por todos
- Directorios sin el bit de ejecución
- Archivos .env o de credenciales con permisos abiertos

FASE 2: POLÍTICA DE PERMISOS
Aplica esta política (muéstrame el plan antes de ejecutar):

| Directorio/archivo    | Propietario  | Permisos |
|----------------------|-------------|----------|
| /var/www/app/        | www-data:www-data | 755 |
| public/              | www-data:www-data | 755 |
| public/* (archivos)  | www-data:www-data | 644 |
| config/              | www-data:www-data | 750 |
| config/* (archivos)  | www-data:www-data | 640 |
| config/.env          | www-data:www-data | 600 |
| logs/                | www-data:www-data | 755 |
| logs/* (archivos)    | www-data:www-data | 644 |
| uploads/             | www-data:www-data | 755 |
| uploads/* (archivos) | www-data:www-data | 644 |
| scripts/*.sh         | www-data:www-data | 750 |

FASE 3: SCRIPT REUTILIZABLE
Genera fix-permisos.sh que:
- Acepta la ruta como parámetro
- Aplica la política anterior
- Muestra los cambios realizados
- Registra todo en un log

FASE 4: VERIFICACIÓN
- Ejecuta el script
- Vuelve a auditar para confirmar que todo está correcto
- Guarda el informe como auditoria-permisos.md
```

---

## Ejercicio 9: Procesamiento de CSV con herramientas CLI

**Prerequisitos:** Un archivo CSV con datos tabulares (al menos 1.000 filas y 8-10 columnas). Pueden ser datos de ventas, logs, inventario o cualquier dataset. Las herramientas necesarias son las estándar de Unix: `awk`, `sort`, `uniq`, `cut`, `paste`, `head`, `tail`, `wc`. No se usa Python ni ningún lenguaje de programación.

**Contexto:** A veces no puedes instalar nada en un servidor y necesitas analizar datos con lo que hay disponible. Este ejercicio demuestra que las herramientas CLI de Unix son suficientes para un análisis completo de datos tabulares.

**Resultado esperado:** Un análisis completo generado exclusivamente con comandos de terminal, con cada comando documentado y explicado.

```text
Analiza el archivo datos.csv usando SOLO herramientas de línea
de comandos. No uses Python, Ruby, Perl ni ningún lenguaje de
programación. Solo: awk, sort, uniq, cut, paste, head, tail,
wc, sed, grep, tr, column.

El archivo tiene estas columnas (ajusta si las tuyas son
diferentes):
id,fecha,cliente,producto,categoria,cantidad,precio_unitario,total,region,estado

ANÁLISIS REQUERIDO:

1. EXPLORACIÓN BÁSICA
   - Número total de filas (sin contar cabecera)
   - Número de columnas
   - Primeras y últimas 5 filas
   - Valores únicos de cada columna categórica
     (categoria, region, estado)

2. ESTADÍSTICAS NUMÉRICAS
   - Suma total de la columna "total"
   - Media, mínimo y máximo de "precio_unitario"
   - Suma de "total" agrupada por "region"
   - Suma de "total" agrupada por "categoria"

3. RANKING
   - Top 10 clientes por volumen de compra
   - Top 5 productos más vendidos (por cantidad)
   - Región con mayor facturación

4. FILTRADO Y BÚSQUEDA
   - Filas donde estado = "pendiente"
   - Filas donde total > 1000
   - Filas del último mes

5. TRANSFORMACIÓN
   - Genera un nuevo CSV solo con las columnas:
     cliente, producto, total, region
   - Ordénalo por total descendente
   - Guárdalo como datos-resumen.csv

Para cada operación, muestra el comando exacto que usas y
explica qué hace. Guarda todos los comandos en un script
analisis-csv.sh que pueda reutilizarse con otros archivos.

Genera también analisis-csv-resultados.md con todos los
resultados formateados.
```

---

## Ejercicio 10: Edición de JSON con jq

**Prerequisitos:** La herramienta `jq` instalada (`apt install jq` o `brew install jq`). Un archivo JSON de configuración (o usa el ejemplo que se genera en el prompt). Este ejercicio trabaja exclusivamente con `jq` para consultar y transformar JSON desde la terminal.

**Contexto:** Muchas aplicaciones modernas usan JSON para configuración, APIs y datos. Saber manipular JSON desde la terminal con `jq` es una habilidad esencial para administradores de sistemas y desarrolladores.

**Resultado esperado:** Una serie de transformaciones documentadas sobre el archivo JSON, con cada comando `jq` explicado paso a paso.

```text
Trabaja con el archivo config.json. Si no existe, créalo primero
con este contenido de ejemplo:

{
  "app": {
    "name": "mi-aplicacion",
    "version": "2.5.0",
    "environment": "production",
    "debug": true
  },
  "database": {
    "host": "db.ejemplo.com",
    "port": 5432,
    "name": "app_production",
    "pool": { "min": 5, "max": 20, "idle_timeout": 30 }
  },
  "cache": {
    "provider": "redis",
    "host": "cache.ejemplo.com",
    "port": 6379,
    "ttl": 3600
  },
  "services": [
    { "name": "auth", "url": "https://auth.ejemplo.com", "timeout": 5000, "enabled": true },
    { "name": "storage", "url": "https://storage.ejemplo.com", "timeout": 10000, "enabled": true },
    { "name": "notifications", "url": "https://notify.ejemplo.com", "timeout": 3000, "enabled": false },
    { "name": "analytics", "url": "https://analytics.ejemplo.com", "timeout": 8000, "enabled": true }
  ],
  "logging": {
    "level": "info",
    "file": "/var/log/app/app.log",
    "max_size_mb": 100,
    "rotate": 7
  }
}

OPERACIONES CON JQ:

1. CONSULTAS (solo lectura)
   - Obtén el nombre y versión de la app
   - Lista todos los servicios habilitados (enabled: true)
   - Muestra el servicio con mayor timeout
   - Extrae solo los nombres de los servicios como array plano
   - Filtra servicios cuyo timeout sea mayor a 5000ms

2. MODIFICACIONES (genera nuevo archivo, no sobrescribas
   el original)
   - Cambia debug a false (es producción)
   - Aumenta el pool máximo de la base de datos a 50
   - Habilita el servicio "notifications"
   - Añade un nuevo servicio:
     { "name": "billing", "url": "https://billing.ejemplo.com",
       "timeout": 15000, "enabled": true }
   - Cambia el nivel de logging a "warn"
   - Guarda como config-production.json

3. TRANSFORMACIONES AVANZADAS
   - Genera un resumen con solo: nombre de app, número de
     servicios habilitados y host de base de datos
   - Convierte el array de servicios a un objeto donde la
     clave sea el nombre del servicio
   - Genera un CSV de servicios: nombre,url,timeout,enabled

4. VALIDACIÓN
   - Compara config.json y config-production.json
   - Muestra solo las diferencias con jq
   - Verifica que config-production.json es JSON válido

Para cada operación, muestra el comando jq exacto y explica
la sintaxis utilizada. Guarda todos los comandos en
jq-operaciones.sh y los resultados en jq-resultados.md.
```
