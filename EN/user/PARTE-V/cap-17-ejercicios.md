# Capítulo 17 — Bases de datos sin miedo: consultar, monitorizar y mantener

Ejercicio guiado en 5 pasos con prompts listos para copiar y pegar en Claude Code o Claude Desktop. El caso completo trabaja con una base de datos SQLite de empresa y llega hasta un informe de negocio completo.

---

## Preparacion: Generar la base de datos de prueba

**Contexto:** Si no tienes acceso a una base de datos real para practicar, este prompt genera una base SQLite completa con datos realistas. La base simula una empresa de servicios con clientes, pedidos, productos, empleados y metricas financieras.

```text
Crea una base de datos SQLite llamada empresa-demo.db con 7 tablas y datos
realistas para una empresa de servicios tecnológicos con 5 años de actividad
(2020-2024).

TABLA 1 — clientes (150 registros)
- id, nombre_empresa, sector (Banca, Seguros, Retail, Industria, Público,
  Telecomunicaciones), tamaño (Pequeña, Mediana, Grande), fecha_alta,
  ciudad, responsable_comercial, estado (Activo, Inactivo, Prospect)

TABLA 2 — productos (25 registros)
- id, nombre, categoría (Consultoría, Desarrollo, Soporte, Formación,
  Licencias), precio_hora, precio_proyecto_medio, margen_objetivo (%),
  activo (sí/no)

TABLA 3 — pedidos (2.500 registros)
- id, cliente_id (FK), producto_id (FK), fecha_pedido, fecha_entrega_prevista,
  fecha_entrega_real (NULL si no entregado), importe, estado (Presupuestado,
  En curso, Entregado, Cancelado, Reclamación), descuento_aplicado (%)

TABLA 4 — empleados (45 registros)
- id, nombre, departamento (Comercial, Delivery, Soporte, Dirección,
  Administración), puesto, fecha_incorporacion, coste_hora, activo (sí/no)

TABLA 5 — asignaciones (3.000 registros)
- id, pedido_id (FK), empleado_id (FK), fecha, horas_dedicadas, tipo_tarea
  (Desarrollo, Consultoría, Gestión, Soporte, Formación)

TABLA 6 — facturas (1.800 registros)
- id, pedido_id (FK), fecha_emision, fecha_vencimiento, importe,
  iva, total, estado (Emitida, Cobrada, Vencida, Anulada)

TABLA 7 — satisfaccion (800 registros)
- id, pedido_id (FK), fecha_encuesta, puntuacion_global (1-10),
  puntuacion_calidad (1-10), puntuacion_plazo (1-10),
  puntuacion_comunicacion (1-10), comentario, recomendaria (sí/no)

RESTRICCIONES:
- Claves foráneas correctas entre todas las tablas
- Índices en campos de búsqueda frecuente (fechas, estados, cliente_id)
- Datos coherentes: las fechas de factura son posteriores a los pedidos,
  los empleados solo tienen asignaciones en fechas posteriores a su
  incorporación, etc.
- Incluye casos problemáticos realistas: 5 pedidos cancelados, 3 con
  reclamación, 12 facturas vencidas no cobradas, 8 pedidos entregados
  fuera de plazo
```

---

## Paso 1 — Explorar el esquema

**Objetivo:** Antes de escribir consultas, entender la estructura completa de la base de datos: tablas, columnas, relaciones y volumen de datos.

```text
Abre la base de datos empresa-demo.db y haz una exploración completa:

1. Lista todas las tablas con su número de filas
2. Para cada tabla, muestra: nombre de columna, tipo de dato,
   si admite NULL, si es clave primaria o foránea
3. Dibuja un diagrama de relaciones entre tablas (en formato texto/ASCII)
4. Para cada tabla, muestra 3 filas de ejemplo
5. Identifica campos con valores NULL y cuenta cuántos hay
6. Verifica la integridad referencial: ¿hay pedidos con cliente_id
   que no existe en la tabla clientes? ¿Facturas de pedidos inexistentes?

Muéstrame todo antes de que yo haga ninguna consulta.
```

---

## Paso 2 — Consultas simples para calentar

**Objetivo:** Empezar con consultas basicas para verificar que la base de datos responde correctamente y familiarizarse con los datos.

### Consulta 2.1 — Resumen rapido

```text
Ejecuta estas consultas sobre empresa-demo.db y muéstrame los resultados
en tablas claras:

1. ¿Cuántos clientes activos hay por sector?
2. ¿Cuál es el top 5 de clientes por importe total de pedidos?
3. ¿Cuántos pedidos hay en cada estado?
```

### Consulta 2.2 — Facturacion basica

```text
Sobre empresa-demo.db:

1. Total facturado por año (2020-2024), con número de facturas
2. Facturas vencidas no cobradas: lista con cliente, importe, días de retraso
3. Importe medio por factura, desglosado por año
```

### Consulta 2.3 — Equipo

```text
Sobre empresa-demo.db:

1. Horas totales dedicadas por cada empleado en 2024
2. ¿Qué empleados tienen más de 1.800 horas anuales? (posible sobrecarga)
3. Distribución de horas por tipo de tarea en el último trimestre
```

---

## Paso 3 — Analisis complejo: ventas de 24 meses

**Objetivo:** Una consulta compleja que cruza varias tablas y genera un analisis temporal detallado. Esto es lo que normalmente requerirta un analista SQL experimentado.

```text
Genera un análisis completo de ventas de los últimos 24 meses (enero 2023
a diciembre 2024) a partir de empresa-demo.db.

El análisis debe cruzar las tablas pedidos, clientes, productos y facturas
y producir:

1. EVOLUCIÓN MENSUAL
   - Tabla mes a mes: pedidos nuevos, importe total, importe medio,
     tasa de cancelación
   - Identifica los 3 mejores meses y los 3 peores
   - Tendencia: ¿las ventas crecen, decrecen o son estables?

2. ANÁLISIS POR SECTOR DE CLIENTE
   - Tabla: sector, número de pedidos, importe total, importe medio,
     % del total
   - ¿Qué sector crece más rápido comparando 2023 vs 2024?
   - ¿Hay algún sector con alta cancelación?

3. ANÁLISIS POR PRODUCTO
   - Tabla: producto, unidades vendidas, importe total, margen real
     vs margen objetivo
   - Productos con margen real inferior al objetivo: ¿por qué?
     (descuentos excesivos, sobrecostes en horas)
   - Productos con tendencia de venta decreciente

4. CICLO DE VENTA
   - Tiempo medio desde pedido hasta entrega (por producto y por sector)
   - Tiempo medio desde entrega hasta cobro
   - ¿Los plazos han mejorado o empeorado en los últimos 6 meses?

5. RETENCIÓN DE CLIENTES
   - ¿Cuántos clientes de 2023 repitieron pedido en 2024?
   - ¿Cuántos clientes nuevos se captaron en 2024?
   - Importe medio de clientes recurrentes vs clientes nuevos

6. CORRELACIÓN SATISFACCIÓN-VENTAS
   - ¿Los clientes con mejor puntuación de satisfacción gastan más?
   - ¿Los clientes con reclamaciones reducen sus pedidos?
   - NPS medio por sector

Muéstrame las consultas SQL que uses (para que pueda reutilizarlas)
y los resultados en tablas formateadas con un párrafo de interpretación
por cada sección.
```

---

## Paso 4 — Chequeo de salud de la base de datos

**Objetivo:** Verificar la calidad e integridad de los datos. En una base de datos real, estos problemas aparecen siempre y detectarlos a tiempo evita errores en los informes.

```text
Ejecuta un chequeo de salud completo sobre empresa-demo.db:

INTEGRIDAD REFERENCIAL
- ¿Hay registros huérfanos? (asignaciones a empleados que no existen,
  facturas de pedidos eliminados, etc.)
- ¿Hay claves foráneas que apuntan a registros inexistentes?

CALIDAD DE DATOS
- Campos que deberían tener valor pero son NULL (ej: pedido entregado
  sin fecha_entrega_real)
- Valores fuera de rango: importes negativos, horas >24 en un día,
  puntuaciones fuera de 1-10
- Fechas incoherentes: factura anterior al pedido, entrega anterior al pedido
- Duplicados potenciales: mismo cliente+producto+fecha+importe

CONSISTENCIA DE NEGOCIO
- ¿El importe de las facturas coincide con el importe del pedido
  (aplicando descuento + IVA)?
- ¿Las horas asignadas a un pedido son coherentes con el importe facturado?
- ¿Hay pedidos en estado "Entregado" sin factura asociada?
- ¿Hay pedidos en estado "Cancelado" con facturas no anuladas?

Genera un informe con:
- Total de problemas encontrados por categoría
- Detalle de cada problema con la consulta SQL que lo detecta
- Nivel de severidad: crítico (afecta a cifras), medio (inconsistencia),
  bajo (dato faltante no esencial)
- Sugerencia de corrección para cada problema
```

---

## Paso 5 — Informe de negocio completo

**Objetivo:** Generar un informe ejecutivo que un director general pueda usar en un comite de direccion, extrayendo toda la informacion relevante de la base de datos.

```text
Usando empresa-demo.db, genera un informe de negocio completo para presentar
en el comité de dirección. El informe debe cubrir 4 secciones:

SECCIÓN 1 — ESTADO FINANCIERO
- Facturación total 2024 vs 2023 (variación absoluta y %)
- Facturación por trimestre con tendencia
- Deuda pendiente de cobro (facturas vencidas): importe y antigüedad media
- Cash-flow simplificado: facturado vs cobrado por mes
- Previsión de cierre de año basada en la tendencia actual

SECCIÓN 2 — OPERACIONES
- Pedidos en curso: número, importe total, fecha prevista de entrega
- Tasa de cumplimiento de plazos (entregas a tiempo vs totales)
- Carga de trabajo del equipo: horas asignadas vs capacidad teórica
- Empleados sobrecargados (>100% capacidad) y empleados infrautilizados (<50%)
- Pedidos con riesgo de retraso (en curso y cerca de fecha límite)

SECCIÓN 3 — COMERCIAL
- Pipeline: pedidos en estado "Presupuestado" (importe y probabilidad)
- Tasa de conversión presupuesto → pedido en firme
- Nuevos clientes captados en el último trimestre
- Clientes en riesgo de pérdida (sin actividad en 6+ meses)
- Top 10 clientes por facturación con tendencia (crecen o decrecen)

SECCIÓN 4 — CALIDAD Y SATISFACCIÓN
- NPS global y por sector
- Evolución de la satisfacción trimestre a trimestre
- Correlación entre satisfacción y renovación de clientes
- Reclamaciones abiertas: número, importe afectado, antigüedad
- Áreas de mejora según los comentarios de las encuestas

Formato: informe en Markdown + un Excel (informe-comite-2024.xlsx) con
cada sección en una hoja y los datos de soporte.
Incluye las consultas SQL principales como apéndice para que el equipo
de datos pueda actualizarlas mensualmente.
```

---

## Ejercicios adicionales (bonus)

### Detectar anomalias

```text
Analiza empresa-demo.db buscando anomalías que podrían indicar problemas
operativos o errores:

1. Pedidos con descuento superior al 30% — ¿quién los aprobó?
   (busca el responsable_comercial del cliente)
2. Clientes con facturación muy concentrada en un solo mes
   (podría indicar dependencia de un solo proyecto grande)
3. Empleados que facturan horas en más de 3 proyectos simultáneamente
4. Productos con margen real negativo (coste en horas > importe facturado)
5. Facturas emitidas más de 30 días después de la entrega del pedido

Para cada anomalía muéstrame: la consulta SQL, los registros afectados
y una recomendación de acción.
```

---

### Crear consultas SQL reutilizables

```text
A partir de los análisis anteriores, genera un fichero consultas-utiles.sql
con las 15 consultas más útiles para el seguimiento mensual del negocio.

Para cada consulta incluye:
- Comentario explicando qué mide y para quién es útil
- La consulta SQL lista para ejecutar
- Ejemplo de resultado esperado (2-3 filas)

Organízalas en secciones:
- Financiero (facturación, cobros, deuda)
- Operativo (plazos, carga de trabajo, estado de pedidos)
- Comercial (pipeline, nuevos clientes, retención)
- Calidad (satisfacción, reclamaciones)

El objetivo es que cualquier persona del equipo pueda ejecutar estas
consultas cada mes sin necesidad de entender SQL complejo.
```
