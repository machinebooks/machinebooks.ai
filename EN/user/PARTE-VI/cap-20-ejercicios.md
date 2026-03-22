# Capítulo 20 — Servidores y servicios

Ejercicios prácticos con prompts listos para copiar y pegar en Claude Code o Claude Desktop.

---

## Ejercicio 1: Diagnóstico de error 502 paso a paso

**Prerequisitos:** Un servidor con Nginx como proxy inverso, una aplicación gestionada por systemd y PostgreSQL como base de datos. El servidor devuelve errores 502 Bad Gateway de forma intermitente. Si no tienes un caso real, puedes simular el fallo deteniendo el servicio de la aplicación mientras Nginx sigue activo.

**Contexto:** El error 502 significa que Nginx no puede comunicarse con el proceso backend. Las causas son múltiples: la aplicación se ha caído, el socket no existe, PostgreSQL no responde, o hay un problema de permisos. Este ejercicio sigue un procedimiento de diagnóstico metódico de tres capas.

**Resultado esperado:** Un informe de diagnóstico con la causa raíz identificada, los comandos ejecutados en cada paso y las acciones correctivas aplicadas.

```text
El servidor web está devolviendo errores 502 Bad Gateway de forma
intermitente. Necesito un diagnóstico completo siguiendo estas
tres capas en orden.

CAPA 1: NGINX (proxy inverso)
- ¿Nginx está corriendo? systemctl status nginx
- Revisa los últimos 50 errores en /var/log/nginx/error.log
- ¿Qué dice el upstream? Busca mensajes "upstream" en el error log
- Verifica la configuración del proxy_pass:
  ¿apunta a un socket o a un puerto? ¿Existe ese socket/puerto?
- Ejecuta nginx -t para verificar la configuración
- Comprueba los timeouts configurados (proxy_connect_timeout,
  proxy_read_timeout)

CAPA 2: APLICACIÓN (servicio systemd)
- ¿El servicio de la aplicación está activo?
  systemctl status mi-aplicacion
- Si está caído, ¿cuándo se cayó y por qué?
  journalctl -u mi-aplicacion --since "1 hour ago"
- ¿El proceso existe? ps aux | grep mi-aplicacion
- ¿Está escuchando en el puerto/socket esperado?
  ss -tlnp | grep <puerto>
- ¿Hay errores de memoria (OOM killer)?
  dmesg | grep -i "killed process"
- ¿Cuántas veces se ha reiniciado hoy?
  systemctl show mi-aplicacion --property=NRestarts

CAPA 3: POSTGRESQL
- ¿PostgreSQL está corriendo? systemctl status postgresql
- ¿Acepta conexiones? pg_isready
- Revisa los últimos errores:
  tail -100 /var/log/postgresql/postgresql-*-main.log
- ¿Hay conexiones bloqueadas?
  SELECT * FROM pg_stat_activity WHERE state = 'idle in transaction';
- ¿La base de datos tiene espacio?
  SELECT pg_database_size('mi_base')/1024/1024 AS size_mb;

SÍNTESIS
Después de revisar las tres capas:
1. Identifica la causa raíz más probable
2. Aplica la corrección inmediata
3. Verifica que el 502 ha desaparecido: curl -I http://localhost
4. Documenta todo en diagnostico-502.md con:
   - Timeline del incidente
   - Comandos ejecutados y salida relevante
   - Causa raíz
   - Corrección aplicada
   - Acciones preventivas para que no vuelva a ocurrir
```

---

## Ejercicio 2: Script de chequeo matutino

**Prerequisitos:** Un servidor Linux con servicios típicos (Nginx, PostgreSQL, Redis, Docker). Acceso a los comandos estándar de monitorización y a `systemctl`. No se requiere instalar software adicional.

**Contexto:** El chequeo matutino es la primera tarea del día para un administrador de sistemas. En vez de ejecutar 15 comandos a mano, este ejercicio genera un script que hace las 6 comprobaciones esenciales y produce un informe Markdown listo para compartir con el equipo.

**Resultado esperado:** Un script bash ejecutable que genera un informe Markdown con formato de semáforo (OK/AVISO/FALLO) para cada comprobación.

```text
Crea un script llamado chequeo-matutino.sh que realice 6
comprobaciones esenciales del servidor y genere un informe
en formato Markdown.

COMPROBACIÓN 1: ESTADO DE SERVICIOS
- Comprueba si están activos: nginx, postgresql, redis-server,
  docker
- Para cada servicio: nombre, estado (activo/inactivo),
  tiempo de actividad
- Semáforo: OK si todos activos, AVISO si alguno reiniciado
  en las últimas 24h, FALLO si alguno inactivo

COMPROBACIÓN 2: USO DE DISCO
- Estado de todas las particiones con df -h
- Semáforo: OK si todas por debajo del 80%, AVISO entre
  80-90%, FALLO por encima del 90%
- Incluir uso de inodos

COMPROBACIÓN 3: MEMORIA Y CPU
- RAM: total, usada, libre, swap
- CPU: carga media (1, 5, 15 min)
- Top 3 procesos por CPU y por RAM
- Semáforo: OK si carga < num_cpus, AVISO si carga < 2×cpus,
  FALLO si carga > 2×cpus

COMPROBACIÓN 4: LOGS DE ERRORES (últimas 12 horas)
- Busca errores críticos en journalctl --priority=err
- Cuenta errores por servicio
- Semáforo: OK si 0 errores, AVISO si < 10, FALLO si > 10

COMPROBACIÓN 5: CONEXIONES DE RED
- Puertos en escucha (ss -tlnp)
- Conexiones establecidas (ss -s)
- Semáforo: OK si los puertos esperados están abiertos,
  FALLO si alguno falta

COMPROBACIÓN 6: SEGURIDAD
- Intentos SSH fallidos en las últimas 12 horas
- Actualizaciones de seguridad pendientes
- Semáforo: OK si < 100 intentos y 0 updates críticas,
  AVISO en caso contrario

FORMATO DEL INFORME
El script debe generar chequeo-YYYY-MM-DD.md con:
- Cabecera con hostname, fecha y hora
- Resumen: 🟢/🟡/🔴 por cada comprobación
- Detalle de cada comprobación
- Sección "Acciones necesarias" solo si hay AVISO o FALLO

REQUISITOS DEL SCRIPT
- Debe funcionar sin parámetros
- Debe poder ejecutarse con cron (sin interacción)
- Incluye manejo de errores (si un comando falla, registra
  el fallo pero continúa con el resto)
- Al final, muestra por pantalla un resumen de una línea:
  "Chequeo completado: 5 OK, 1 AVISO, 0 FALLO"
```

---

## Ejercicio 3: Diagnóstico de rendimiento lento (4 capas)

**Prerequisitos:** Un servidor que muestra tiempos de respuesta lentos en su aplicación web. Acceso a las herramientas del sistema (`top`, `vmstat`, `iostat`, `ss`), logs de Nginx, PostgreSQL y Redis. Si no tienes un caso real, puedes provocar carga con `stress-ng` o `ab` (Apache Benchmark).

**Contexto:** "El servidor va lento" es la queja más frecuente y la más difícil de diagnosticar porque las causas pueden estar en cualquier capa. Este ejercicio sigue un enfoque sistemático de 4 capas para aislar el cuello de botella.

**Resultado esperado:** Un informe de diagnóstico que identifica la capa causante del problema, con métricas concretas y acciones correctivas priorizadas.

```text
La aplicación web responde con tiempos de 5-10 segundos cuando
normalmente tarda menos de 500ms. Diagnostica el problema
siguiendo estas 4 capas en orden estricto. NO saltes a
conclusiones hasta revisar todas las capas.

CAPA 1: SISTEMA OPERATIVO
- Carga del sistema: uptime
- CPU por proceso: top -bn1 | head -20
- Memoria: free -h
- Swap: ¿se está usando? Si el swap está activo, es probable
  que haya presión de memoria
- I/O de disco: iostat -x 1 3
  ¿Hay algún disco con %util > 80%?
- Procesos en estado D (esperando I/O): ps aux | awk '$8=="D"'
- Resumen de capa 1: ¿El cuello de botella está en el SO?
  (CPU / memoria / disco / ninguno)

CAPA 2: NGINX
- Conexiones activas: curl http://localhost/nginx_status
  (o ss -s)
- ¿Hay peticiones en cola? Revisa los logs de acceso:
  peticiones con tiempo > 3s
- Worker processes: ¿cuántos hay y cuántos están ocupados?
- Errores upstream en las últimas horas
- Resumen de capa 2: ¿Nginx es el cuello de botella?

CAPA 3: POSTGRESQL
- Conexiones activas:
  SELECT count(*), state FROM pg_stat_activity GROUP BY state;
- Consultas lentas (> 1 segundo):
  SELECT pid, now()-query_start AS duration, query
  FROM pg_stat_activity WHERE state='active'
  AND now()-query_start > interval '1 second';
- Bloqueos:
  SELECT * FROM pg_locks WHERE NOT granted;
- Cache hit ratio:
  SELECT sum(heap_blks_hit)/sum(heap_blks_hit+heap_blks_read)
  FROM pg_statio_user_tables;
  (Si es menor de 0.95, la BD necesita más memoria)
- Resumen de capa 3: ¿PostgreSQL es el cuello de botella?

CAPA 4: REDIS
- ¿Está respondiendo? redis-cli ping
- Memoria usada: redis-cli info memory
- Latencia: redis-cli --latency -c 10
- Comandos lentos: redis-cli slowlog get 10
- Conexiones: redis-cli info clients
- Resumen de capa 4: ¿Redis es el cuello de botella?

DIAGNÓSTICO FINAL
Genera diagnostico-rendimiento.md con:
1. Tabla resumen de las 4 capas (estado de cada una)
2. Capa identificada como cuello de botella
3. Evidencia concreta (métricas que lo prueban)
4. Acciones correctivas inmediatas (prioridad 1)
5. Acciones preventivas a medio plazo (prioridad 2)
6. Métricas a monitorizar para detectarlo antes la
   próxima vez
```

---

## Ejercicio 4: Generación de informe post-mortem

**Prerequisitos:** Que haya ocurrido un incidente reciente (o simulado) en el servidor. Los datos del incidente: cuándo empezó, cuándo se detectó, qué servicios se vieron afectados y cuándo se resolvió. Acceso a los logs del periodo del incidente.

**Contexto:** Un post-mortem bien escrito es la herramienta más valiosa para evitar que un incidente se repita. Este ejercicio guía al agente para recopilar la información del incidente directamente de los logs y generar un documento profesional con el formato estándar de la industria.

**Resultado esperado:** Un documento post-mortem completo en Markdown, con timeline preciso extraído de logs, causa raíz verificable y acciones correctivas con responsable y fecha límite.

```text
Genera un informe post-mortem del incidente ocurrido entre las
[HORA_INICIO] y las [HORA_FIN] de hoy. Sustituye las horas
por el rango real del incidente.

RECOPILACIÓN DE DATOS
Antes de escribir nada, recopila esta información:

1. Logs del sistema durante el incidente:
   journalctl --since "HORA_INICIO" --until "HORA_FIN"

2. Logs de Nginx:
   Filtra access.log y error.log en ese rango de tiempo

3. Logs de la aplicación:
   journalctl -u mi-aplicacion --since "HORA_INICIO" --until "HORA_FIN"

4. Logs de PostgreSQL en ese periodo

5. Métricas del sistema durante el incidente:
   sar (si está disponible) o reconstruye a partir de logs

ESTRUCTURA DEL POST-MORTEM

# Post-Mortem: [Título descriptivo del incidente]
Fecha: [hoy]
Duración: [HORA_INICIO] - [HORA_FIN] (X minutos)
Severidad: [Crítica/Alta/Media]
Redactado por: [hostname del servidor]

## Resumen ejecutivo
(3-4 líneas: qué pasó, a quién afectó, cuánto duró)

## Timeline del incidente
(Tabla con timestamp y evento, extraído de los logs reales.
Cada entrada debe tener la fuente: nginx, app, postgresql, system)

| Hora  | Evento | Fuente |
|-------|--------|--------|
| HH:MM | ...    | ...    |

## Impacto
- Usuarios afectados (estimación a partir de los logs de acceso)
- Peticiones fallidas durante el incidente
- Servicios afectados
- Pérdida de datos (si aplica)

## Causa raíz
(Explicación técnica de qué causó el incidente, con evidencia
de los logs)

## Detección
- ¿Cómo se detectó? (alerta automática, reporte de usuario,
  revisión manual)
- Tiempo entre inicio e incidente y detección
- ¿Deberíamos haberlo detectado antes? ¿Cómo?

## Resolución
- Pasos tomados para resolver el incidente
- ¿Qué funcionó y qué no?
- Tiempo de resolución

## Acciones correctivas
(Tabla con acción, responsable, fecha límite, estado)

| # | Acción | Prioridad | Fecha límite |
|---|--------|-----------|-------------|
| 1 | ...    | ...       | ...         |

## Lecciones aprendidas
- ¿Qué salió bien?
- ¿Qué salió mal?
- ¿Qué tuvimos suerte de que no pasara?

Guarda como postmortem-YYYY-MM-DD.md
```

---

## Ejercicio 5: Script de diagnóstico rápido parametrizado

**Prerequisitos:** Acceso a un servidor Linux con los comandos estándar de administración. Este ejercicio genera un script reutilizable que acepta parámetros para diagnosticar problemas específicos.

**Contexto:** Cuando un servidor tiene problemas, los primeros 5 minutos son críticos. Este script recopila toda la información relevante de forma rápida y parametrizada, para que cualquier miembro del equipo pueda ejecutarlo sin necesidad de recordar 20 comandos distintos.

**Resultado esperado:** Un script bash que acepta un modo de diagnóstico como parámetro y genera un informe específico para ese tipo de problema.

```text
Crea un script llamado diagnostico.sh que acepte un parámetro
indicando el tipo de problema y ejecute el diagnóstico
correspondiente.

USO:
  ./diagnostico.sh [modo]

MODOS DISPONIBLES:

  cpu     → Diagnóstico de CPU
           - top 10 procesos por CPU
           - carga media histórica (si hay datos de sar)
           - procesos en estado zombie
           - hilos por proceso

  memoria → Diagnóstico de memoria
           - RAM desglosada (total, usada, cache, disponible)
           - Swap: uso y qué procesos la están usando
           - Top 10 procesos por RSS
           - OOM killer: ¿ha matado algo? (dmesg)

  disco   → Diagnóstico de disco
           - Espacio por partición
           - Inodos por partición
           - Top 10 directorios más grandes en /var y /home
           - Archivos abiertos pero eliminados (lsof +L1)
           - I/O por proceso (si iotop está disponible)

  red     → Diagnóstico de red
           - Interfaces y sus IPs
           - Tabla de rutas
           - Puertos en escucha con proceso asociado
           - Conexiones por estado (ESTABLISHED, TIME_WAIT, etc.)
           - Resolución DNS: ¿funciona?
           - Latencia a los gateways

  todo    → Ejecuta los 4 modos anteriores

REQUISITOS DEL SCRIPT:
- Si se ejecuta sin parámetros, muestra la ayuda
- Cada modo genera su sección en el informe
- El informe se guarda como diagnostico-[modo]-YYYY-MM-DD-HHMM.md
- Los errores de comandos no disponibles se registran pero no
  detienen la ejecución
- Tiempo total de ejecución al final del informe
- El script no debe requerir instalación de paquetes adicionales
```

---

## Ejercicio 6: Revisión de cambios recientes en el servidor (48h)

**Prerequisitos:** Un servidor Linux en producción (o desarrollo) donde se hayan realizado cambios recientemente. Acceso a los logs del sistema, historial de paquetes y ficheros de configuración.

**Contexto:** Cuando algo falla después de un cambio, lo más difícil es saber exactamente qué se cambió. Este ejercicio recopila todos los cambios realizados en las últimas 48 horas: paquetes actualizados, archivos de configuración modificados, servicios reiniciados y despliegues de la aplicación.

**Resultado esperado:** Un informe cronológico de todos los cambios detectados en el servidor, con evaluación de riesgo para cada uno.

```text
Investiga todos los cambios realizados en este servidor en las
últimas 48 horas. Necesito saber exactamente qué se modificó,
cuándo y quién lo hizo (si es posible determinarlo).

1. PAQUETES DEL SISTEMA
   - ¿Se instalaron o actualizaron paquetes?
     Debian/Ubuntu: grep "install\|upgrade" /var/log/dpkg.log
     CentOS/RHEL: yum history (o dnf history)
   - Lista con: fecha, acción, paquete, versión anterior,
     versión nueva

2. ARCHIVOS DE CONFIGURACIÓN MODIFICADOS
   - Busca archivos en /etc/ modificados en las últimas 48h:
     find /etc -mtime -2 -type f
   - Para cada archivo modificado, intenta mostrar el diff si
     hay backup (.bak, .old, .orig)
   - Presta especial atención a:
     /etc/nginx/, /etc/postgresql/, /etc/ssh/,
     /etc/systemd/, /etc/crontab

3. SERVICIOS REINICIADOS
   - Revisa journalctl por reinicios de servicios en las
     últimas 48h
   - ¿Algún servicio se reinició de forma inesperada (crasheó)?
   - ¿Se habilitaron o deshabilitaron servicios?

4. DESPLIEGUES DE APLICACIÓN
   - Busca archivos modificados recientemente en /var/www/,
     /opt/, /srv/ o donde esté la aplicación
   - Revisa logs de Docker si hay contenedores:
     docker ps -a --format "table {{.Names}}\t{{.Status}}\t{{.CreatedAt}}"
   - ¿Se recrearon contenedores o imágenes?

5. USUARIOS Y ACCESOS
   - Último acceso de cada usuario: lastlog
   - Sesiones de las últimas 48h: last -48
   - ¿Se crearon o modificaron usuarios?
     find /etc/passwd /etc/shadow /etc/group -mtime -2

6. TAREAS PROGRAMADAS
   - ¿Se modificó algún crontab en las últimas 48h?
   - ¿Hay nuevas tareas en /etc/cron.d/?

INFORME FINAL
Genera cambios-servidor-48h.md con:
- Tabla cronológica de todos los cambios detectados
- Clasificación de riesgo: bajo/medio/alto
- Correlación: ¿algún cambio coincide con el inicio de un
  problema reportado?
- Recomendaciones: ¿algún cambio debería revertirse?
```

---

## Ejercicio 7: Revisión de certificados SSL

**Prerequisitos:** Un servidor con certificados SSL instalados (Let's Encrypt, certificados comerciales o autofirmados). Acceso a `openssl` y a los directorios de certificados (`/etc/letsencrypt/`, `/etc/ssl/`, `/etc/nginx/ssl/`).

**Contexto:** Los certificados caducados son una de las causas más frecuentes de interrupciones en producción. Este ejercicio audita todos los certificados del servidor, comprueba su validez y genera alertas para los que caduquen pronto.

**Resultado esperado:** Un inventario completo de certificados con su estado de validez, alertas para los que caducan en los próximos 30 días y un script de monitorización automática.

```text
Realiza una auditoría completa de los certificados SSL de este
servidor.

PASO 1: INVENTARIO DE CERTIFICADOS
Busca todos los certificados en el servidor:
- /etc/letsencrypt/live/*/fullchain.pem
- /etc/ssl/certs/ (solo los que no sean del sistema)
- /etc/nginx/ssl/
- Cualquier ruta referenciada en las configuraciones de Nginx:
  grep -r "ssl_certificate" /etc/nginx/

Para cada certificado encontrado, extrae con openssl:
- Dominio principal (CN) y dominios alternativos (SAN)
- Fecha de emisión (Not Before)
- Fecha de caducidad (Not After)
- Emisor (Issuer)
- Algoritmo de firma
- Longitud de clave

PASO 2: ESTADO DE CADA CERTIFICADO
Clasifica cada certificado:
- VÁLIDO: caduca en más de 30 días
- ATENCIÓN: caduca en 15-30 días
- URGENTE: caduca en menos de 15 días
- CADUCADO: ya expiró

PASO 3: VERIFICACIÓN DE CADENA
Para cada certificado activo en Nginx:
- Verifica la cadena completa:
  openssl verify -CAfile ca-bundle certificado.pem
- Comprueba que el certificado coincide con la clave privada
- Verifica que el servidor responde correctamente:
  openssl s_client -connect dominio:443

PASO 4: SCRIPT DE MONITORIZACIÓN
Crea check-ssl.sh que:
- Comprueba todos los certificados encontrados
- Envía alerta (por stdout o correo) si alguno caduca
  en menos de 30 días
- Puede ejecutarse con cron diariamente
- Registra el resultado en /var/log/ssl-check.log

PASO 5: INFORME
Genera auditoria-ssl.md con:
- Tabla de todos los certificados con su estado
- Certificados que necesitan acción inmediata
- Certificados de Let's Encrypt: ¿la renovación automática
  funciona? Comprueba con: certbot renew --dry-run
- Recomendaciones de seguridad (algoritmos débiles, claves
  cortas, etc.)
```

---

## Ejercicio 8: Chequeo de seguridad básico

**Prerequisitos:** Acceso con permisos de administrador al servidor. Este ejercicio NO es una auditoría profesional de seguridad, pero cubre las comprobaciones básicas que todo administrador debería hacer periódicamente.

**Contexto:** La seguridad de un servidor empieza por lo básico: saber quién tiene acceso, qué puertos están abiertos, qué permisos tienen los archivos críticos y quién ha intentado entrar sin autorización. Este ejercicio cubre las 4 áreas fundamentales.

**Resultado esperado:** Un informe de seguridad básico con hallazgos clasificados por severidad y acciones correctivas concretas.

```text
Realiza un chequeo de seguridad básico del servidor cubriendo
estas 4 áreas. Para cada hallazgo, clasifícalo como:
CRÍTICO, ALTO, MEDIO, BAJO o INFO.

ÁREA 1: USUARIOS Y ACCESO SSH
- Lista todos los usuarios con shell de login
  (no los de sistema con /sbin/nologin):
  awk -F: '$7 != "/sbin/nologin" && $7 != "/usr/sbin/nologin"
  && $7 != "/bin/false" {print $1,$7}' /etc/passwd
- ¿Hay usuarios con UID 0 además de root?
- ¿Está habilitado el login de root por SSH?
  Revisa /etc/ssh/sshd_config: PermitRootLogin
- ¿Se usa autenticación por contraseña en SSH?
  PasswordAuthentication
- ¿Hay claves SSH autorizadas para cada usuario?
  Revisa ~/.ssh/authorized_keys de cada usuario con shell
- ¿Los permisos de .ssh/ y authorized_keys son correctos?
  (.ssh = 700, authorized_keys = 600)

ÁREA 2: PUERTOS ABIERTOS Y SERVICIOS
- Puertos TCP en escucha: ss -tlnp
- Puertos UDP en escucha: ss -ulnp
- Para cada puerto, identifica:
  - Qué proceso lo abre
  - Si está escuchando en 0.0.0.0 (todas las interfaces)
    o solo en 127.0.0.1 (local)
- Marca como ALTO los servicios que escuchan en 0.0.0.0
  y no deberían (bases de datos, Redis, servicios internos)
- ¿Hay firewall activo? iptables -L -n o ufw status

ÁREA 3: PERMISOS DE ARCHIVOS CRÍTICOS
Verifica los permisos de:
- /etc/shadow (debe ser 640, root:shadow)
- /etc/sudoers (debe ser 440, root:root)
- /etc/ssh/sshd_config (debe ser 600, root:root)
- Claves privadas SSH del servidor /etc/ssh/ssh_host_*_key
  (deben ser 600, root:root)
- Archivos .env de aplicaciones (no deben ser legibles
  por todos)
- Busca archivos SUID sospechosos:
  find / -perm -4000 -type f 2>/dev/null
- Busca directorios con escritura para todos en rutas
  sensibles: find /etc /var/www -perm -o+w -type d

ÁREA 4: INTENTOS DE ACCESO FALLIDOS
- Intentos SSH fallidos en las últimas 72 horas
  (auth.log o secure)
- Top 10 IPs con más intentos fallidos
- ¿Hay algún usuario válido del sistema entre los intentados?
- ¿Está fail2ban u otra protección activa?
  systemctl status fail2ban
- Últimos accesos exitosos: last -20
- Intentos de sudo fallidos: grep "FAILED" /var/log/auth.log

INFORME FINAL
Genera chequeo-seguridad.md con:

1. Resumen ejecutivo (semáforo general)
2. Tabla de hallazgos:
   | # | Área | Severidad | Hallazgo | Acción correctiva |
3. Comandos para corregir cada hallazgo CRÍTICO y ALTO
4. Recomendaciones generales de hardening
5. Sugerencia de frecuencia para repetir este chequeo
```
