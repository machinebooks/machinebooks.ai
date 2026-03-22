# Capítulo 22 — Contenedores y despliegues

Ejercicios prácticos con prompts listos para copiar y pegar en Claude Code o Claude Desktop.

---

## Ejercicio 1: Ciclo de vida con Docker Compose

**Prerequisitos:** Docker y Docker Compose instalados. Un archivo `docker-compose.yml` con al menos 4-6 servicios (por ejemplo: aplicación web, base de datos, cache, cola de tareas, proxy inverso y servicio de búsqueda). Si no tienes uno propio, crea un `docker-compose.yml` de ejemplo con los 6 servicios antes de empezar.

**Contexto:** Gestionar el ciclo de vida de una aplicación multi-contenedor es una tarea diaria. Este ejercicio cubre la secuencia completa: parada controlada, reconstrucción de imágenes, arranque y verificación de que los 6 servicios están sanos. El orden importa, porque algunos servicios dependen de otros.

**Resultado esperado:** Los 6 servicios detenidos, reconstruidos y arrancados en el orden correcto, con verificación de salud de cada uno y un log del proceso completo.

```text
Gestiona el ciclo de vida completo de la aplicación Docker
Compose. El archivo está en /ruta/a/tu/proyecto/docker-compose.yml
(ajusta la ruta).

Los 6 servicios esperados son (adapta los nombres a tu caso):
1. nginx (proxy inverso)
2. app (aplicación web)
3. postgres (base de datos)
4. redis (cache)
5. worker (procesador de cola)
6. search (motor de búsqueda)

PASO 1: ESTADO ACTUAL
- docker compose ps (estado de todos los servicios)
- docker compose logs --tail=20 (últimas líneas de cada uno)
- docker system df (uso de disco de Docker)

PASO 2: PARADA CONTROLADA
Para los servicios en el orden correcto (de fuera a dentro):
1. Detener nginx (deja de recibir tráfico)
2. Detener worker (termina las tareas en curso)
3. Detener app (la aplicación)
4. Detener search
5. Detener redis
6. Detener postgres (último, porque otros dependen de él)

Usa: docker compose stop [servicio] para cada uno.
Verifica entre cada parada que el servicio anterior se
detuvo correctamente.

PASO 3: RECONSTRUCCIÓN
- Reconstruye las imágenes sin usar cache:
  docker compose build --no-cache
- Si alguna imagen falla al construir, muestra el error
  y sugiere la corrección antes de continuar
- Muestra el tamaño de cada imagen nueva vs la anterior

PASO 4: ARRANQUE
Arranca en el orden inverso (de dentro a fuera):
1. postgres → espera a que acepte conexiones
2. redis → espera a PONG
3. search → espera a que el health check pase
4. app → espera a que responda en su puerto
5. worker → verifica que conecta con redis
6. nginx → verifica que el proxy funciona

Usa: docker compose up -d [servicio] para cada uno.

PASO 5: VERIFICACIÓN
Para cada servicio, confirma que está sano:
- docker compose ps (todos deben estar "Up" o "healthy")
- Prueba de conectividad:
  curl -s http://localhost (a través de nginx)
- Logs de los últimos 30 segundos de cada servicio:
  ¿hay errores?
- docker compose exec postgres pg_isready
- docker compose exec redis redis-cli ping

PASO 6: DOCUMENTACIÓN
Guarda un log completo del proceso como deploy-log.md con:
- Hora de inicio y fin de cada paso
- Estado antes y después
- Cualquier error encontrado y cómo se resolvió
- Espacio de disco antes y después
```

---

## Ejercicio 2: Diagnóstico de contenedor en bucle de reinicios

**Prerequisitos:** Docker Compose con al menos un servicio que esté reiniciándose continuamente (estado "Restarting" en `docker compose ps`). Si no tienes un caso real, simúlalo creando un servicio cuyo comando de inicio falle (por ejemplo, una aplicación que intenta conectar a una base de datos que no existe).

**Contexto:** Un contenedor en bucle de reinicios es uno de los problemas más frustrantes de Docker. El contenedor arranca, falla, Docker lo reinicia, vuelve a fallar... y los logs se sobrescriben con cada reinicio. Este ejercicio enseña a diagnosticar la causa raíz de forma metódica.

**Resultado esperado:** La causa raíz identificada, el contenedor reparado y estable, y un documento con el procedimiento de diagnóstico para referencia futura.

```text
Uno de los contenedores de Docker Compose está en un bucle de
reinicios. Diagnostica y repara el problema.

PASO 1: IDENTIFICAR EL CONTENEDOR
- docker compose ps
  Identifica qué servicio(s) tienen estado "Restarting" o
  "Exit X" (donde X es el código de salida)
- Anota el código de salida:
  - 0: terminó correctamente (posible problema de configuración)
  - 1: error de aplicación
  - 137: OOM killed (sin memoria)
  - 139: segfault
  - 143: SIGTERM (Docker lo detuvo)

PASO 2: LOGS DEL CONTENEDOR
- docker compose logs --tail=100 [servicio]
- Si los logs se repiten con cada reinicio, busca las
  primeras líneas de error de cada ciclo
- docker inspect [contenedor_id] --format='{{.State.Error}}'
- ¿El error es de conexión (a BD, Redis, etc.)?
- ¿Es un error de permisos?
- ¿Es un error de configuración (variable de entorno faltante)?
- ¿Es un error de espacio en disco?

PASO 3: INVESTIGACIÓN PROFUNDA
Dependiendo del error encontrado:

Si es conexión rechazada:
- ¿El servicio destino está corriendo?
- ¿Están en la misma red Docker?
  docker network inspect [red]
- ¿El nombre del host es correcto en la configuración?
- ¿El puerto es el correcto?

Si es OOM (código 137):
- ¿Hay límites de memoria en docker-compose.yml?
- docker stats --no-stream [contenedor]
- ¿Necesita más memoria o tiene un memory leak?

Si es error de aplicación (código 1):
- docker compose run --rm [servicio] sh
  (entra en un contenedor nuevo sin arrancar la app)
- Verifica que los archivos de configuración existen
- Verifica variables de entorno:
  docker compose config | grep [servicio] -A 20

Si es permisos:
- ¿Los volúmenes montados tienen los permisos correctos?
- ¿El usuario dentro del contenedor puede leer/escribir?

PASO 4: REPARACIÓN
- Aplica la corrección (modifica docker-compose.yml,
  variables de entorno, permisos, etc.)
- Reconstruye si es necesario: docker compose build [servicio]
- Arranca: docker compose up -d [servicio]
- Monitoriza durante 2 minutos: docker compose logs -f [servicio]
- Confirma que no se reinicia más:
  docker compose ps (debe mostrar "Up X minutes" sin reinicios)

PASO 5: DOCUMENTACIÓN
Genera diagnostico-restart-loop.md con:
- Servicio afectado y código de salida
- Causa raíz encontrada
- Pasos de diagnóstico seguidos
- Corrección aplicada
- Cómo prevenir que vuelva a ocurrir
```

---

## Ejercicio 3: Despliegue con Kubernetes y rollback

**Prerequisitos:** Un clúster de Kubernetes accesible con `kubectl` configurado. Un Deployment existente llamado `api-server` (o el nombre que uses) que va a actualizarse a la versión v2.5.0. Si no tienes un clúster real, puedes usar Minikube o kind para crear uno local.

**Contexto:** El despliegue progresivo (rolling deployment) de Kubernetes permite actualizar una aplicación sin tiempo de inactividad. Pero si la nueva versión falla, hay que saber hacer rollback rápidamente. Este ejercicio cubre el ciclo completo: actualización, monitorización y rollback si es necesario.

**Resultado esperado:** El Deployment actualizado a v2.5.0 con verificación de que todos los pods están sanos, o un rollback exitoso a la versión anterior si la nueva versión falla.

```text
Realiza un despliegue rolling de api-server a la versión v2.5.0
en Kubernetes con capacidad de rollback.

PRE-DESPLIEGUE: ESTADO ACTUAL
- Anota la versión actual:
  kubectl get deployment api-server -o jsonpath='{.spec.template.spec.containers[0].image}'
- Pods actuales:
  kubectl get pods -l app=api-server -o wide
- ¿Están todos Ready y Running?
- Historial de despliegues anteriores:
  kubectl rollout history deployment/api-server
- Verifica que la aplicación funciona:
  kubectl exec -it [pod] -- curl -s http://localhost:8080/health

PASO 1: CONFIGURAR ESTRATEGIA DE DESPLIEGUE
Antes de actualizar, verifica o ajusta la estrategia rolling:
  kubectl get deployment api-server -o yaml | grep -A5 strategy

Valores recomendados:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1

Si no está configurado así, aplica el cambio con:
  kubectl patch deployment api-server -p '{"spec":{"strategy":...}}'

PASO 2: EJECUTAR EL DESPLIEGUE
- Actualiza la imagen:
  kubectl set image deployment/api-server
    api-server=tu-registro/api-server:v2.5.0
- Monitoriza el progreso en tiempo real:
  kubectl rollout status deployment/api-server
- En paralelo, observa los pods:
  kubectl get pods -l app=api-server -w

PASO 3: VERIFICACIÓN POST-DESPLIEGUE
Espera a que el rollout complete y verifica:
- Todos los pods están Running y Ready:
  kubectl get pods -l app=api-server
- La nueva versión está desplegada:
  kubectl describe deployment api-server | grep Image
- La aplicación responde correctamente:
  kubectl exec -it [nuevo-pod] -- curl -s http://localhost:8080/health
- Los logs no muestran errores:
  kubectl logs -l app=api-server --tail=50
- Los endpoints del servicio son correctos:
  kubectl get endpoints api-server

PASO 4: ROLLBACK (si algo falla)
Si la verificación falla o los pods no arrancan:
- Inmediatamente:
  kubectl rollout undo deployment/api-server
- Monitoriza el rollback:
  kubectl rollout status deployment/api-server
- Verifica que la versión anterior está restaurada:
  kubectl get deployment api-server -o jsonpath='{.spec.template.spec.containers[0].image}'
- Confirma que la aplicación funciona:
  kubectl exec -it [pod] -- curl -s http://localhost:8080/health

PASO 5: DOCUMENTACIÓN
Genera despliegue-api-server-v250.md con:
- Versión anterior y nueva
- Hora de inicio y fin del despliegue
- Resultado: éxito o rollback
- Si hubo rollback: causa del fallo y acciones para
  corregir la v2.5.0 antes del próximo intento
- Checklist para el próximo despliegue
```

---

## Ejercicio 4: Documento de procedimiento de despliegue

**Prerequisitos:** Una aplicación desplegada con Docker Compose o Kubernetes. Conocimiento de los servicios que la componen, sus dependencias y el proceso actual de despliegue (aunque sea informal). Este ejercicio no ejecuta el despliegue, sino que documenta el procedimiento.

**Contexto:** Si la persona que hace los despliegues no está disponible, el equipo debe poder seguir un procedimiento documentado. Este ejercicio genera un documento de procedimiento profesional que cualquier miembro del equipo pueda seguir paso a paso.

**Resultado esperado:** Un documento Markdown completo con el procedimiento de despliegue, checklists, comandos exactos y procedimientos de rollback.

```text
Genera un documento de procedimiento de despliegue completo
para la aplicación. Analiza primero la infraestructura actual
y después documenta el proceso.

ANÁLISIS PREVIO
Recopila esta información del entorno:
- docker compose ps (o kubectl get all)
- Servicios y sus versiones actuales
- Variables de entorno configuradas (sin valores sensibles)
- Volúmenes y datos persistentes
- Redes configuradas

DOCUMENTO DE PROCEDIMIENTO
Estructura el documento así:

# Procedimiento de despliegue — [Nombre de la aplicación]
Última actualización: [fecha]
Autor: [hostname]
Versión del procedimiento: 1.0

## 1. Información general
- Arquitectura: diagrama en texto de los servicios y
  sus dependencias
- Servicios críticos vs opcionales
- Tiempo estimado del despliegue completo

## 2. Pre-requisitos
- Accesos necesarios (SSH, registro de contenedores, etc.)
- Herramientas que deben estar instaladas
- Backups que deben existir antes de empezar

## 3. Checklist pre-despliegue
(Lista de verificación con checkboxes)
- [ ] Backup de la base de datos realizado
- [ ] Versión anterior anotada para rollback
- [ ] Tests pasados en el entorno de staging
- [ ] Equipo notificado del despliegue
- [ ] Ventana de mantenimiento programada (si aplica)
- [ ] Monitorización preparada para observar el despliegue

## 4. Procedimiento paso a paso
Para cada paso:
- Descripción de qué se hace y por qué
- Comando exacto a ejecutar
- Resultado esperado
- Qué hacer si falla

## 5. Verificación post-despliegue
- Checklist de verificaciones con los comandos
- Pruebas funcionales mínimas
- Métricas a observar durante los 30 minutos siguientes

## 6. Procedimiento de rollback
- Paso a paso para volver a la versión anterior
- Tiempo estimado del rollback
- Datos que podrían perderse en un rollback

## 7. Contactos y escalación
- Quién contactar si algo falla
- Niveles de escalación

## 8. Historial de despliegues
(Tabla para registrar cada despliegue futuro)
| Fecha | Versión | Responsable | Resultado | Notas |

Guarda como procedimiento-despliegue.md
```

---

## Ejercicio 5: Gestión de Secrets en Kubernetes

**Prerequisitos:** Un clúster de Kubernetes con `kubectl` configurado. Familiaridad básica con el concepto de Secrets en Kubernetes. Si no tienes un clúster real, puedes usar Minikube.

**Contexto:** Los Secrets de Kubernetes almacenan datos sensibles como contraseñas, tokens y certificados. Aunque Kubernetes los codifica en base64 (no es cifrado), gestionarlos correctamente es fundamental para la seguridad. Este ejercicio cubre la creación, uso, rotación y auditoría de Secrets.

**Resultado esperado:** Secrets creados y vinculados a los pods correctos, un procedimiento de rotación documentado y una auditoría del estado actual de los Secrets del clúster.

```text
Gestiona los Secrets de Kubernetes de forma segura.

PASO 1: AUDITORÍA DE SECRETS EXISTENTES
- Lista todos los Secrets del namespace actual:
  kubectl get secrets
- Para cada Secret, muestra su tipo y antigüedad:
  kubectl get secrets -o custom-columns=
    NAME:.metadata.name,TYPE:.type,AGE:.metadata.creationTimestamp
- Identifica Secrets no utilizados (no referenciados por
  ningún Pod, Deployment o StatefulSet):
  Para cada Secret, busca si algún recurso lo referencia
- Identifica Secrets con más de 90 días sin rotar

PASO 2: CREAR SECRETS DE FORMA SEGURA
Crea los siguientes Secrets (usa valores de ejemplo):

a) Secret para la base de datos:
   kubectl create secret generic db-credentials \
     --from-literal=username=app_user \
     --from-literal=password=GENERA_PASSWORD_SEGURO \
     --from-literal=host=postgres.default.svc.cluster.local \
     --from-literal=port=5432

b) Secret para la API externa:
   kubectl create secret generic api-keys \
     --from-literal=claude-api-key=sk-ant-EJEMPLO \
     --from-literal=storage-key=EJEMPLO

c) Secret TLS a partir de certificados:
   kubectl create secret tls app-tls \
     --cert=ruta/al/cert.pem \
     --key=ruta/a/la/key.pem

PASO 3: VINCULAR SECRETS A DEPLOYMENTS
Muestra cómo referenciar los Secrets creados en un Deployment:

a) Como variables de entorno:
   Genera el fragmento YAML que inyecta db-credentials
   como variables de entorno en el contenedor

b) Como volumen montado:
   Genera el fragmento YAML que monta api-keys como
   archivos en /etc/secrets/

c) Como imagePullSecret (para registros privados)

PASO 4: PROCEDIMIENTO DE ROTACIÓN
Documenta el procedimiento para rotar un Secret:
1. Crear el nuevo Secret con un nombre temporal
2. Actualizar el Deployment para usar el nuevo Secret
3. Verificar que los pods nuevos funcionan
4. Eliminar el Secret antiguo
5. Renombrar si es necesario

Genera un script rotar-secret.sh que automatice este proceso
aceptando como parámetros: nombre del Secret, clave a rotar
y nuevo valor.

PASO 5: SEGURIDAD Y BUENAS PRÁCTICAS
Genera un informe gestion-secrets-k8s.md con:
- Inventario actual de Secrets
- Secrets que necesitan rotación
- Secrets no utilizados (candidatos a eliminar)
- Recomendaciones:
  - Habilitar cifrado en reposo (EncryptionConfiguration)
  - Limitar acceso con RBAC
  - Considerar herramientas externas (Vault, Sealed Secrets)
  - Política de rotación recomendada
```

---

## Ejercicio 6: Depuración avanzada de contenedores

**Prerequisitos:** Docker o Kubernetes con contenedores en ejecución. Este ejercicio requiere poder ejecutar comandos dentro de los contenedores (`docker exec` o `kubectl exec`). Los contenedores deben tener al menos las herramientas básicas de red y sistema (algunos contenedores minimalistas basados en `scratch` o `distroless` no las incluyen).

**Contexto:** Cuando algo falla dentro de un contenedor, necesitas entrar y diagnosticar desde dentro. Pero los contenedores suelen tener herramientas limitadas, los sistemas de archivos son efímeros y la red está virtualizada. Este ejercicio enseña técnicas de depuración adaptadas al entorno de contenedores.

**Resultado esperado:** Diagnóstico completo de un contenedor con problemas, ejecutado desde dentro del contenedor y desde el host, con las técnicas documentadas para referencia futura.

```text
Diagnostica problemas dentro de contenedores Docker usando
técnicas avanzadas de depuración.

ESCENARIO: El contenedor de la aplicación (app) se comporta de
forma anómala — responde lento, consume más memoria de lo
habitual o devuelve errores intermitentes.

TÉCNICA 1: EXPLORACIÓN DESDE DENTRO
Entra en el contenedor:
  docker compose exec app sh (o bash si está disponible)

Dentro del contenedor:
- ¿Qué proceso corre? ps aux
- ¿Cuánta memoria usa? cat /proc/meminfo
- ¿Qué archivos tiene abiertos? ls -la /proc/1/fd/ | wc -l
- ¿Las variables de entorno son correctas? env | sort
- ¿Los archivos de configuración existen y tienen el
  contenido esperado?
- ¿Puede resolver DNS? nslookup postgres (o getent hosts)
- ¿Puede conectar con la base de datos?
  Si no hay cliente de BD, usa:
  echo "SELECT 1" | nc postgres 5432
- ¿Puede conectar con Redis?
  echo PING | nc redis 6379

TÉCNICA 2: INSPECCIÓN DESDE EL HOST
Sin entrar en el contenedor:
- Procesos del contenedor vistos desde el host:
  docker top [contenedor]
- Estadísticas en tiempo real:
  docker stats [contenedor] --no-stream
- Cambios en el sistema de archivos (respecto a la imagen):
  docker diff [contenedor]
- Inspección completa:
  docker inspect [contenedor] | jq '.[]|{
    State, NetworkSettings.Networks, Mounts,
    Config.Env, HostConfig.Memory}'

TÉCNICA 3: CONTENEDOR DE DEPURACIÓN
Si el contenedor no tiene herramientas, usa un contenedor
auxiliar en la misma red:
  docker run -it --rm --network [red_del_compose] \
    nicolaka/netshoot sh

Desde netshoot (tiene todas las herramientas de red):
- ping app
- curl http://app:8080/health
- dig postgres
- nmap -sT app -p 8080
- tcpdump -i any host app

TÉCNICA 4: ANÁLISIS DE LOGS AVANZADO
- Logs con timestamps:
  docker compose logs --timestamps app | tail -100
- Buscar patrones de error:
  docker compose logs app 2>&1 | grep -i "error\|exception\|fatal"
- Correlacionar logs entre servicios:
  docker compose logs --timestamps 2>&1 | sort | grep "ERROR"

TÉCNICA 5: SISTEMA DE ARCHIVOS Y VOLÚMENES
- Verificar que los volúmenes están montados:
  docker inspect [contenedor] --format='{{json .Mounts}}' | jq
- Verificar permisos dentro del contenedor:
  docker compose exec app ls -la /datos /config /logs
- Comprobar espacio disponible:
  docker compose exec app df -h

DOCUMENTACIÓN
Genera debug-contenedores.md con:
- Cada técnica usada y resultado obtenido
- Causa raíz identificada (si aplica)
- Referencia rápida de comandos de depuración
- Qué herramientas añadir al Dockerfile para facilitar
  el diagnóstico futuro (sin comprometer la seguridad)
```

---

## Ejercicio 7: Limpieza de imágenes Docker

**Prerequisitos:** Docker instalado con historial de uso (imágenes, contenedores parados, volúmenes huérfanos). Este ejercicio es especialmente útil cuando Docker consume demasiado espacio en disco. Precaución: antes de limpiar, asegúrate de que no hay datos importantes en volúmenes huérfanos.

**Contexto:** Docker acumula imágenes antiguas, contenedores parados, volúmenes huérfanos y capas de cache que pueden consumir decenas o cientos de GB de disco. Este ejercicio limpia de forma controlada y segura, documentando cada paso para evitar borrar algo necesario.

**Resultado esperado:** Espacio de disco recuperado, inventario de lo que se eliminó y un script de limpieza programable para mantenimiento periódico.

```text
Realiza una limpieza completa y segura de Docker.

FASE 1: DIAGNÓSTICO DE USO DE DISCO
- Resumen general:
  docker system df
- Detalle por tipo:
  docker system df -v

Genera una tabla con:
| Tipo | Cantidad | Espacio total | Espacio recuperable |
| Imágenes | ... | ... | ... |
| Contenedores | ... | ... | ... |
| Volúmenes | ... | ... | ... |
| Build cache | ... | ... | ... |

FASE 2: INVENTARIO ANTES DE LIMPIAR

a) Contenedores parados:
   docker ps -a --filter status=exited --format
     "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Size}}"
   ¿Alguno tiene datos importantes? Comprueba volúmenes
   asociados antes de eliminar.

b) Imágenes sin usar (dangling):
   docker images -f dangling=true
   Estas son capas intermedias que no pertenecen a ninguna
   imagen etiquetada. Seguro eliminarlas.

c) Imágenes antiguas:
   docker images --format "{{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.CreatedSince}}"
   Identifica versiones antiguas de las mismas imágenes.

d) Volúmenes huérfanos:
   docker volume ls -f dangling=true
   PRECAUCIÓN: pueden contener datos de base de datos.
   Para cada volumen, intenta identificar a qué servicio
   pertenecía.

e) Redes sin usar:
   docker network ls
   docker network prune --dry-run

FASE 3: LIMPIEZA CONTROLADA (pide confirmación en cada paso)

Paso 1: Eliminar contenedores parados:
  docker container prune
  Espacio recuperado: X

Paso 2: Eliminar imágenes dangling:
  docker image prune
  Espacio recuperado: X

Paso 3: Eliminar imágenes antiguas (versiones anteriores):
  Para cada imagen con múltiples tags, conserva solo
  la más reciente y elimina las anteriores:
  docker rmi [imagen:tag_antiguo]

Paso 4: Eliminar volúmenes huérfanos (solo los seguros):
  docker volume rm [volumen]
  (solo después de confirmar que no contienen datos
  importantes)

Paso 5: Limpiar build cache:
  docker builder prune

FASE 4: RESULTADO
- docker system df (después de la limpieza)
- Comparativa antes/después
- Espacio total recuperado

FASE 5: SCRIPT DE MANTENIMIENTO
Genera limpieza-docker.sh que:
- Muestra el espacio antes de limpiar
- Elimina contenedores parados de más de 7 días
- Elimina imágenes dangling
- Elimina imágenes sin usar de más de 30 días:
  docker image prune -a --filter "until=720h"
- Limpia build cache de más de 7 días
- NO toca volúmenes (demasiado riesgo)
- Muestra el espacio después
- Registra todo en /var/log/docker-cleanup.log

Sugiere una entrada de cron para ejecutarlo semanalmente.

Guarda como:
- limpieza-docker.sh (el script)
- limpieza-docker-informe.md (el informe de esta ejecución)
```
