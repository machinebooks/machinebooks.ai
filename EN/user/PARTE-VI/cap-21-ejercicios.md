# Capítulo 21 — La nube desde el CLI

Ejercicios prácticos con prompts listos para copiar y pegar en Claude Code o Claude Desktop.

---

## Ejercicio 1: Informe de costes AWS y optimización

**Prerequisitos:** AWS CLI configurado con credenciales que tengan permisos de lectura sobre Cost Explorer, EC2, RDS y S3 (`aws configure` completado). Los permisos necesarios incluyen `ce:GetCostAndUsage`, `ec2:Describe*`, `rds:Describe*` y `s3:List*`. Si no tienes acceso real a AWS, puedes adaptar el ejercicio a la documentación de tu cuenta o usar datos de ejemplo.

**Contexto:** La factura de AWS crece silenciosamente. Este ejercicio genera un informe completo de costes con recomendaciones de ahorro concretas. El objetivo es detectar recursos infrautilizados, instancias sobredimensionadas y oportunidades de optimización antes de que la factura sorprenda a fin de mes.

**Resultado esperado:** Un informe Markdown con 6 secciones que cubren el análisis de costes, recursos ociosos y un plan de ahorro con estimación de impacto económico.

```text
Genera un informe completo de costes de la cuenta AWS y propón
un plan de optimización. Usa AWS CLI para obtener todos los datos.

SECCIÓN 1: RESUMEN DE COSTES (último mes)
- Coste total del último mes completo:
  aws ce get-cost-and-usage --time-period Start=YYYY-MM-01,End=YYYY-MM-31 \
    --granularity MONTHLY --metrics BlendedCost
- Desglose por servicio (top 10):
  aws ce get-cost-and-usage ... --group-by Type=DIMENSION,Key=SERVICE
- Comparativa con el mes anterior (variación porcentual)
- Tendencia: ¿los costes suben, bajan o se mantienen?

SECCIÓN 2: INSTANCIAS EC2
- Lista todas las instancias con tipo, estado, región y nombre:
  aws ec2 describe-instances --query
    "Reservations[].Instances[].{ID:InstanceId,Type:InstanceType,
    State:State.Name,AZ:Placement.AvailabilityZone,
    Name:Tags[?Key=='Name'].Value|[0]}"
- Identifica instancias detenidas (stopped) que siguen
  teniendo volúmenes EBS vinculados (generan coste)
- Identifica instancias con utilización de CPU < 10%
  (si CloudWatch está disponible)

SECCIÓN 3: ALMACENAMIENTO
- Volúmenes EBS no vinculados a ninguna instancia:
  aws ec2 describe-volumes --filters Name=status,Values=available
- Snapshots antiguos (más de 90 días):
  aws ec2 describe-snapshots --owner-ids self
- Buckets S3 con su tamaño estimado:
  Para cada bucket: aws s3 ls s3://bucket --summarize --recursive
  (si hay muchos, limitar a los 10 más grandes)

SECCIÓN 4: BASES DE DATOS RDS
- Instancias RDS con tipo, motor y estado:
  aws rds describe-db-instances
- ¿Hay instancias RDS sin conexiones activas?
- ¿Hay instancias Multi-AZ que no lo necesitan (desarrollo)?
- Snapshots RDS manuales antiguos

SECCIÓN 5: OTROS SERVICIOS
- Elastic IPs no asociadas (generan coste):
  aws ec2 describe-addresses --query
    "Addresses[?AssociationId==null]"
- Load Balancers sin targets registrados
- NAT Gateways activos (son caros: ~32 USD/mes cada uno)

SECCIÓN 6: PLAN DE OPTIMIZACIÓN
Genera una tabla de acciones ordenadas por ahorro estimado:

| # | Acción | Recurso | Ahorro mensual estimado | Riesgo | Esfuerzo |
|---|--------|---------|------------------------|--------|----------|

Incluye al menos estas categorías:
- Eliminar recursos ociosos (IPs, volúmenes, snapshots)
- Redimensionar instancias infrautilizadas
- Apagar instancias de desarrollo fuera de horario
- Migrar a instancias Spot o Reserved donde aplique
- Mover datos fríos a S3 Glacier

Ahorro total estimado al final del informe.
Guarda como informe-costes-aws.md
```

---

## Ejercicio 2: Gestión de instancias EC2 y script de apagado automático

**Prerequisitos:** AWS CLI configurado con permisos de EC2 (`ec2:Describe*`, `ec2:StartInstances`, `ec2:StopInstances`). Al menos 2-3 instancias EC2 en la cuenta (pueden ser las del entorno de desarrollo). Acceso para configurar cron en la máquina local o en una instancia de gestión.

**Contexto:** Las instancias de desarrollo y pruebas suelen dejarse encendidas fuera del horario laboral, acumulando costes innecesarios. Este ejercicio gestiona el ciclo de vida de las instancias y crea un script de apagado automático programado con cron.

**Resultado esperado:** Un inventario de instancias, un script de apagado/encendido automático y la configuración de cron correspondiente.

```text
Gestiona las instancias EC2 de la cuenta y crea un sistema de
apagado automático para reducir costes.

PASO 1: INVENTARIO
Lista todas las instancias EC2 con:
  aws ec2 describe-instances --output table --query
    "Reservations[].Instances[].{
      ID:InstanceId,
      Nombre:Tags[?Key=='Name'].Value|[0],
      Tipo:InstanceType,
      Estado:State.Name,
      IP:PublicIpAddress,
      AZ:Placement.AvailabilityZone,
      Lanzamiento:LaunchTime
    }"

Clasifica cada instancia:
- PRODUCCIÓN: instancias que deben estar siempre encendidas
  (identifica por tag Environment=production o por nombre)
- DESARROLLO: instancias que pueden apagarse fuera de horario
- PARADAS: instancias stopped que podrían eliminarse

PASO 2: SCRIPT DE APAGADO AUTOMÁTICO
Crea auto-ec2.sh que:
- Acepta dos modos: "stop" y "start"
- Filtra instancias por tag Environment=development
  (o el tag que identifique las de desarrollo)
- En modo "stop": para todas las instancias de desarrollo
  que estén running
- En modo "start": arranca todas las instancias de desarrollo
  que estén stopped
- Registra cada acción con timestamp
- Envía un resumen por stdout (para capturarlo con cron)
- Tiene modo --dry-run que muestra qué haría sin ejecutar

Ejemplo de uso:
  ./auto-ec2.sh stop          # Para las de desarrollo
  ./auto-ec2.sh start         # Las enciende
  ./auto-ec2.sh stop --dry-run # Solo muestra el plan

PASO 3: CONFIGURACIÓN DE CRON
Genera las entradas de cron para:
- Apagar desarrollo: lunes a viernes a las 20:00
- Encender desarrollo: lunes a viernes a las 07:30
- Informe semanal de costes EC2: domingos a las 10:00

Explica cómo instalar el cron:
  crontab -e

PASO 4: ESTIMACIÓN DE AHORRO
Calcula el ahorro mensual estimado:
- Horas encendidas actualmente (24×30 = 720h/mes)
- Horas con apagado automático (12h × 22 días laborables = 264h/mes)
- Coste por hora de cada tipo de instancia
- Ahorro = (720 - 264) × coste_hora × num_instancias

Guarda todo en:
- inventario-ec2.md (paso 1)
- auto-ec2.sh (paso 2)
- cron-ec2.txt (paso 3, con las líneas listas para copiar)
```

---

## Ejercicio 3: Auditoría de seguridad en la nube

**Prerequisitos:** AWS CLI configurado con permisos de lectura amplios (política `ReadOnlyAccess` o equivalente). Los servicios principales que se auditarán son: IAM, EC2 (Security Groups), S3 y CloudTrail.

**Contexto:** Los errores de configuración en la nube son la causa principal de brechas de seguridad. Un bucket S3 público, un grupo de seguridad demasiado permisivo o un usuario IAM con credenciales sin rotar pueden tener consecuencias graves. Este ejercicio realiza 5 comprobaciones de seguridad fundamentales.

**Resultado esperado:** Un informe de auditoría de seguridad con hallazgos clasificados por severidad, acciones correctivas y un script para repetir la auditoría periódicamente.

```text
Realiza una auditoría de seguridad de la cuenta AWS. Para cada
hallazgo, clasifícalo como CRÍTICO, ALTO, MEDIO o BAJO.

CHECK 1: IDENTIDAD Y ACCESO (IAM)
- Usuarios IAM con credenciales de consola sin MFA:
  aws iam get-credential-report (genéralo primero si no existe)
  Filtra usuarios donde mfa_active = false y
  password_enabled = true
- Access keys sin rotar en más de 90 días:
  aws iam list-access-keys para cada usuario
  Compara con la fecha actual
- Políticas demasiado permisivas:
  ¿Algún usuario o rol tiene AdministratorAccess?
  aws iam list-attached-user-policies para cada usuario
- Cuenta root: ¿tiene access keys activas?
  (CRÍTICO si las tiene)
- Usuarios sin actividad en más de 90 días

CHECK 2: GRUPOS DE SEGURIDAD
- Security groups con puertos abiertos a 0.0.0.0/0:
  aws ec2 describe-security-groups --query
    "SecurityGroups[].{ID:GroupId,Name:GroupName,
    Rules:IpPermissions[?contains(IpRanges[].CidrIp,'0.0.0.0/0')]}"
- CRÍTICO si: puerto 22 (SSH), 3389 (RDP), 3306 (MySQL),
  5432 (PostgreSQL) o 6379 (Redis) abiertos al mundo
- ALTO si: cualquier otro puerto abierto al mundo
- Security groups no utilizados (no asociados a ninguna ENI)

CHECK 3: ALMACENAMIENTO S3
- Buckets con acceso público:
  Para cada bucket, verifica:
  aws s3api get-public-access-block --bucket nombre
  aws s3api get-bucket-policy --bucket nombre
  aws s3api get-bucket-acl --bucket nombre
- Buckets sin cifrado por defecto:
  aws s3api get-bucket-encryption --bucket nombre
- Buckets sin versionado (riesgo de pérdida de datos):
  aws s3api get-bucket-versioning --bucket nombre

CHECK 4: LOGS Y MONITORIZACIÓN
- ¿CloudTrail está activo?
  aws cloudtrail describe-trails
- ¿Cubre todas las regiones?
- ¿Los logs se guardan en un bucket con acceso restringido?
- ¿Hay alertas de CloudWatch configuradas para eventos
  de seguridad? (cambios en IAM, login de root, etc.)

CHECK 5: RED
- VPCs con configuraciones por defecto sin modificar
- Subnets públicas: ¿tienen instancias que no deberían
  ser públicas?
- Flow logs: ¿están habilitados en las VPCs principales?
  aws ec2 describe-flow-logs

INFORME
Genera auditoria-seguridad-aws.md con:
1. Resumen ejecutivo con semáforo general
2. Tabla de hallazgos por severidad
3. Comandos para corregir cada hallazgo CRÍTICO y ALTO
4. Script check-seguridad-aws.sh que repita estas 5
   comprobaciones de forma automatizada
5. Recomendación de frecuencia: semanal para los checks
   críticos, mensual para el informe completo
```

---

## Ejercicio 4: Análisis de almacenamiento S3 y migración a Glacier

**Prerequisitos:** AWS CLI configurado con permisos de S3 (`s3:List*`, `s3:GetObject`, `s3:PutBucketLifecycleConfiguration`). Al menos un bucket S3 con datos variados (distintas antigüedades y tamaños). Si no tienes datos reales, crea un bucket de prueba con carpetas que simulen distintas antigüedades.

**Contexto:** El almacenamiento en S3 Standard tiene un coste razonable, pero cuando los datos crecen y gran parte son archivos antiguos que nadie consulta, la migración a clases de almacenamiento más baratas (Glacier, Deep Archive) puede reducir los costes de almacenamiento en un 80-90%. Este ejercicio analiza los datos y calcula el ahorro exacto.

**Resultado esperado:** Un análisis detallado del uso de S3 por bucket y antigüedad, un cálculo de ahorro con distintos escenarios de migración y las políticas de ciclo de vida configuradas.

```text
Analiza el almacenamiento S3 de la cuenta y calcula el ahorro
de migrar datos antiguos a Glacier.

FASE 1: INVENTARIO DE BUCKETS
Para cada bucket de la cuenta:
  aws s3api list-buckets

Para cada bucket, obtén:
- Nombre y región
- Número total de objetos:
  aws s3api list-objects-v2 --bucket NOMBRE --query
    "length(Contents)"
- Tamaño total:
  aws s3 ls s3://NOMBRE --summarize --recursive | tail -2
- Clase de almacenamiento actual de los objetos
- Fecha del objeto más antiguo y del más reciente

Si hay muchos buckets, limítate a los 10 más grandes.

FASE 2: ANÁLISIS POR ANTIGÜEDAD
Para los buckets principales, clasifica los objetos por
antigüedad:
- Últimos 30 días (datos activos)
- 30-90 días (datos recientes)
- 90-180 días (datos tibios)
- 180-365 días (datos fríos)
- Más de 1 año (datos archivables)

Para cada rango, calcula:
- Número de objetos
- Tamaño total
- Porcentaje sobre el total del bucket

FASE 3: CÁLCULO DE COSTES Y AHORRO
Usa estos precios de referencia (us-east-1, ajusta si
tu región es diferente):
- S3 Standard:       0,023 USD/GB/mes
- S3 Infrequent Access: 0,0125 USD/GB/mes
- S3 Glacier Instant: 0,004 USD/GB/mes
- S3 Glacier Flexible: 0,0036 USD/GB/mes
- S3 Glacier Deep Archive: 0,00099 USD/GB/mes

Calcula 3 escenarios:

Escenario A (conservador):
- >1 año → Glacier Flexible
- Todo lo demás queda en Standard

Escenario B (moderado):
- 180-365 días → Infrequent Access
- >1 año → Glacier Flexible

Escenario C (agresivo):
- 90-180 días → Infrequent Access
- 180-365 días → Glacier Instant Retrieval
- >1 año → Glacier Deep Archive

Para cada escenario: coste mensual actual, coste después
de la migración, ahorro mensual y anual.

FASE 4: POLÍTICAS DE CICLO DE VIDA
Para el escenario elegido, genera la configuración de
lifecycle policy:
  aws s3api put-bucket-lifecycle-configuration --bucket NOMBRE \
    --lifecycle-configuration file://lifecycle.json

Genera el archivo lifecycle.json con las reglas.
Explica cada regla y cuándo se aplicará.

FASE 5: INFORME
Guarda como analisis-s3-glacier.md con:
- Inventario de buckets (tabla)
- Distribución por antigüedad (tabla + porcentajes)
- Comparativa de los 3 escenarios (tabla de costes)
- Escenario recomendado y justificación
- Configuración de lifecycle lista para aplicar
- Advertencias: tiempos de recuperación en Glacier,
  costes de retrieval, objetos que no deben migrarse
```

---

## Ejercicio 5: Comparativa multi-proveedor (Azure + GCP)

**Prerequisitos:** Acceso CLI a al menos dos proveedores cloud. Idealmente: AWS CLI (`aws`), Azure CLI (`az`) y Google Cloud CLI (`gcloud`). Si solo tienes acceso a uno, el ejercicio puede adaptarse comparando la información real de un proveedor con los precios públicos de los otros dos.

**Contexto:** Muchas organizaciones usan más de un proveedor cloud o evalúan migrar de uno a otro. Este ejercicio compara los tres grandes proveedores para un escenario concreto: desplegar una aplicación web con base de datos, cache, almacenamiento de objetos y CDN.

**Resultado esperado:** Una comparativa detallada de precios, servicios equivalentes y recomendaciones para el escenario especificado.

```text
Genera una comparativa detallada entre AWS, Azure y GCP para
desplegar una aplicación web con estos requisitos:

ESCENARIO BASE:
- 2 servidores de aplicación (4 vCPU, 16 GB RAM)
- 1 base de datos gestionada PostgreSQL (4 vCPU, 16 GB RAM,
  100 GB almacenamiento)
- 1 servicio de cache Redis (6 GB RAM)
- 500 GB de almacenamiento de objetos
- CDN con 1 TB de transferencia mensual
- Balanceador de carga

COMPARATIVA 1: SERVICIOS EQUIVALENTES
Genera una tabla con el servicio equivalente en cada proveedor:

| Componente | AWS | Azure | GCP |
|-----------|-----|-------|-----|
| Compute   | EC2 | Virtual Machines | Compute Engine |
| BD PostgreSQL | RDS | Azure Database | Cloud SQL |
| Cache Redis | ElastiCache | Azure Cache | Memorystore |
| Almacenamiento | S3 | Blob Storage | Cloud Storage |
| CDN | CloudFront | Azure CDN | Cloud CDN |
| Balanceador | ALB | Azure LB | Cloud LB |

COMPARATIVA 2: PRECIOS MENSUALES
Para cada proveedor, calcula el coste mensual de cada
componente usando las calculadoras de precios o los precios
públicos más recientes.

Usa estos comandos donde estén disponibles:
- AWS: aws pricing get-products (si tienes acceso)
- Azure: az vm list-sizes --location westeurope
- GCP: gcloud compute machine-types list

Si no tienes acceso directo a precios, usa los precios
públicos de las páginas de precios de cada proveedor
(región Europa Occidental o equivalente).

Incluye:
- Precio bajo demanda (on-demand)
- Precio con compromiso de 1 año
- Precio con compromiso de 3 años

COMPARATIVA 3: CARACTERÍSTICAS TÉCNICAS
Para cada servicio clave, compara:
- SLA garantizado
- Regiones disponibles en Europa
- Opciones de escalado automático
- Backup incluido o con coste adicional
- Herramientas de monitorización nativas

COMPARATIVA 4: TRANSFERENCIA DE DATOS
(El coste oculto de la nube)
- Coste de egress (salida de datos) por GB para cada proveedor
- Coste de transferencia entre regiones
- Coste de transferencia entre zonas de disponibilidad
- Tráfico gratuito incluido en cada proveedor

COMPARATIVA 5: CLI Y AUTOMATIZACIÓN
Compara la experiencia de administración por CLI:
- Sintaxis para las 5 operaciones más comunes
  (crear VM, listar recursos, ver logs, crear bucket,
  gestionar permisos)
- Facilidad de scripting
- Terraform: ¿soporte completo en los tres?

INFORME FINAL
Genera comparativa-cloud.md con:
- Tabla resumen de costes mensuales por proveedor
- Proveedor más económico para este escenario
- Proveedor con mejor relación calidad-precio
- Factores no económicos a considerar (ecosistema,
  soporte, comunidad, herramientas)
- Recomendación final con justificación
- Nota: incluir disclaimer de que los precios son
  orientativos y deben verificarse en las calculadoras
  oficiales de cada proveedor
```
