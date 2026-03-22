# Capítulo 24 — Pipelines de datos: encadenar fases con Claude

Ejercicios prácticos para construir pipelines de procesamiento de datos donde Claude ejecuta cada fase secuencialmente, con validaciones entre pasos.

---

## Ejercicio 1: Pipeline de reporting financiero mensual

**Prerequisitos:** Cuatro archivos CSV con datos financieros del mes. Claude Code instalado con acceso al directorio de trabajo.

**Contexto:** El cierre financiero mensual requiere consolidar datos de múltiples fuentes, validarlos, analizarlos y producir un informe para dirección. Este pipeline divide el proceso en cuatro fases con puntos de control entre cada una.

### Paso A — Preparar los datos de entrada

Crea la estructura de carpetas y los archivos CSV:

```
pipeline-financiero/
├── entrada/
│   ├── facturacion_mes.csv      ← columnas: Fecha, NumFactura, Cliente, Concepto, BaseImponible, IVA, Total, Estado
│   ├── gastos_mes.csv           ← columnas: Fecha, Proveedor, Categoria, Concepto, Importe, FormaPago, Aprobado
│   ├── presupuesto_mes.csv      ← columnas: Partida, PresupuestoAsignado, GastoAcumulado, Disponible
│   └── cobros_mes.csv           ← columnas: Fecha, NumFactura, Cliente, ImporteCobrado, MetodoPago, DiasDesdeEmision
├── intermedio/                   ← archivos generados entre fases
├── salida/                       ← informe final
└── CLAUDE.md
```

### Paso B — El prompt completo del pipeline

Crea el archivo `CLAUDE.md` con las instrucciones. Este es el prompt que define las cuatro fases:

```markdown
# Pipeline de reporting financiero mensual

Ejecuta las siguientes fases en orden. No avances a la siguiente fase si la actual tiene errores.

## FASE 1 — Obtener y validar datos

Lee los cuatro archivos CSV de la carpeta `entrada/`:
- facturacion_mes.csv
- gastos_mes.csv
- presupuesto_mes.csv
- cobros_mes.csv

Para cada archivo, verifica:
1. Que el archivo existe y no está vacío.
2. Que las columnas esperadas están presentes (ver nombres arriba).
3. Que los campos numéricos contienen valores numéricos válidos.
4. Que las fechas tienen formato consistente (DD/MM/YYYY o YYYY-MM-DD).
5. Que no hay filas completamente duplicadas.

Genera el archivo `intermedio/validacion.md` con:
- Estado de cada archivo: OK o ERROR con detalle.
- Número de filas por archivo.
- Filas con problemas detectados (máximo 10 ejemplos por archivo).
- Decisión: CONTINUAR si todos los archivos pasan, o PARAR si hay errores críticos.

Si algún archivo tiene errores críticos (no existe, columnas incorrectas, más del 10% de filas con datos inválidos), detente aquí y no ejecutes las fases siguientes.

## FASE 2 — Limpiar y preparar

A partir de los datos validados en Fase 1:

1. Elimina filas duplicadas de todos los archivos.
2. Normaliza fechas al formato YYYY-MM-DD.
3. Redondea todos los importes a 2 decimales.
4. En facturacion_mes.csv: verifica que Total = BaseImponible + IVA (tolerancia de 0.01 EUR). Marca las filas que no cuadren.
5. En gastos_mes.csv: filtra solo los gastos con Aprobado = "Sí".
6. Cruza cobros_mes.csv con facturacion_mes.csv por NumFactura:
   - Identifica facturas emitidas pero no cobradas.
   - Identifica cobros sin factura correspondiente (posibles errores).

Genera los archivos limpios en `intermedio/`:
- facturacion_limpia.csv
- gastos_aprobados.csv
- cobros_cruzados.csv (con columna adicional: EstadoCobro = Cobrada/Pendiente/SinFactura)
- discrepancias.csv (todas las filas con problemas de cuadre o cruces fallidos)

## FASE 3 — Analizar

Con los datos limpios de la Fase 2, calcula:

**Facturación:**
- Total facturado en el mes (suma de Total).
- Facturación por cliente (tabla ordenada de mayor a menor).
- Top 5 clientes por importe.
- Media de importe por factura.
- Facturas en estado pendiente de cobro: número e importe total.
- Antigüedad media de las facturas pendientes (días desde emisión).

**Gastos:**
- Total de gastos aprobados.
- Gastos por categoría (tabla con importe y porcentaje del total).
- Top 3 proveedores por gasto.
- Gasto medio por operación.

**Presupuesto:**
- Ejecución presupuestaria: porcentaje gastado vs asignado por partida.
- Partidas con desviación superior al 10% (sobreejecutadas o infraejecutadas).
- Presupuesto total disponible.

**Tesorería:**
- Ratio de cobro: importe cobrado / importe facturado.
- Plazo medio de cobro (DiasDesdeEmision de las facturas cobradas).
- Previsión de cobros pendientes (facturas emitidas no cobradas).

Guarda todos los cálculos en `intermedio/analisis_completo.json`.

## FASE 4 — Generar informe

Con el análisis de la Fase 3, genera el informe final en `salida/informe_financiero_YYYY-MM.md`:

1. RESUMEN EJECUTIVO (8-10 líneas)
   - Facturación total, gastos totales y resultado operativo (facturación - gastos).
   - Ratio de cobro y alerta si es inferior al 80%.
   - Ejecución presupuestaria global.
   - El dato más relevante del mes (positivo o negativo).

2. FACTURACIÓN (tabla de clientes + gráfico de evolución si hay datos de meses anteriores)

3. GASTOS POR CATEGORÍA (tabla + porcentaje)

4. EJECUCIÓN PRESUPUESTARIA (tabla con semáforo: verde <90%, amarillo 90-100%, rojo >100%)

5. ESTADO DE TESORERÍA
   - Cobros realizados vs pendientes.
   - Facturas con más de 60 días sin cobrar (alerta).

6. DISCREPANCIAS Y ALERTAS
   - Filas que no cuadraban en la validación.
   - Cobros sin factura.
   - Desviaciones presupuestarias significativas.

7. RECOMENDACIONES (3-5 puntos accionables)

Tono ejecutivo: datos primero, interpretación después. Sin rodeos.
```

### Paso C — Ejecutar el pipeline

```bash
cd /ruta/a/pipeline-financiero
claude -p "Ejecuta el pipeline completo siguiendo las instrucciones de CLAUDE.md. Procesa las cuatro fases en orden y no avances si una fase falla."
```

**Qué observar:**
- Los archivos intermedios permiten auditar qué ocurrió en cada fase.
- Si la Fase 1 detecta errores, el pipeline se detiene antes de producir análisis sobre datos incorrectos.
- El archivo `discrepancias.csv` es la trazabilidad de todo lo que no cuadra.

---

## Ejercicio 2: Pipeline de análisis de satisfacción de clientes

**Prerequisitos:** Un archivo CSV con encuestas de satisfacción del trimestre. Claude Code instalado.

**Contexto:** Los datos de satisfacción de clientes suelen llegar en bruto desde formularios online. Este pipeline calcula el NPS, identifica clientes en riesgo y extrae áreas de mejora a partir de los comentarios de texto libre.

### Paso A — Preparar los datos

Crea el archivo de entrada con esta estructura:

```
satisfaccion/
├── entrada/
│   └── encuestas-q1.csv
├── salida/
└── CLAUDE.md
```

El CSV `encuestas-q1.csv` debe tener estas columnas:

```
FechaRespuesta, ClienteID, NombreCliente, Sector, Pregunta1_Recomendacion (0-10), Pregunta2_Calidad (1-5), Pregunta3_Soporte (1-5), Pregunta4_Precio (1-5), ComentarioLibre, AntiguedadMeses
```

### Paso B — El prompt completo

```text
Ejecuta el pipeline de análisis de satisfacción de clientes con los datos
del archivo entrada/encuestas-q1.csv.

FASE 1 — VALIDACIÓN Y LIMPIEZA
- Verifica que todas las respuestas tienen ClienteID y al menos la Pregunta1.
- Descarta respuestas duplicadas del mismo ClienteID (conserva la más reciente).
- Verifica rangos: Pregunta1 entre 0-10, Preguntas 2-4 entre 1-5.
- Marca respuestas fuera de rango como inválidas.
- Genera un resumen de validación: total recibidas, válidas, descartadas y motivos.

FASE 2 — CÁLCULO DE NPS (Net Promoter Score)
Usa Pregunta1_Recomendacion para clasificar:
- Promotores: 9-10
- Pasivos: 7-8
- Detractores: 0-6

Calcula:
- NPS global = (% Promotores - % Detractores)
- NPS por sector de cliente
- NPS por antigüedad (segmentos: <12 meses, 12-36 meses, >36 meses)
- Distribución completa de puntuaciones (histograma en texto)

FASE 3 — IDENTIFICACIÓN DE CLIENTES EN RIESGO
Un cliente está en riesgo si cumple AL MENOS DOS de estos criterios:
- Pregunta1 (recomendación) <= 5
- Pregunta3 (soporte) <= 2
- ComentarioLibre contiene palabras negativas (cancelar, problema, inaceptable,
  decepción, alternativa, cambiar de proveedor, insatisfecho)
- Caída de puntuación respecto al trimestre anterior (si hay datos)

Genera la lista de clientes en riesgo ordenada por gravedad, con:
- Nombre, sector, antigüedad
- Puntuaciones en las 4 preguntas
- Fragmento relevante del comentario
- Motivos por los que se considera en riesgo

FASE 4 — ÁREAS DE MEJORA
Analiza todos los ComentarioLibre:
- Extrae los temas más mencionados (agrupa sinónimos: "soporte/atención/ayuda",
  "precio/coste/tarifa", "velocidad/lentitud/tiempo de respuesta").
- Para cada tema: número de menciones, sentimiento predominante (positivo/negativo/neutro),
  ejemplos representativos (2-3 citas textuales).
- Identifica las 3 áreas prioritarias de mejora basándote en frecuencia + impacto en NPS.

INFORME FINAL
Genera en salida/informe_satisfaccion_Q1.md:
1. Resumen ejecutivo (NPS, tendencia, dato más relevante)
2. NPS desglosado (tablas por sector y antigüedad)
3. Mapa de satisfacción (tabla con medias de las 4 preguntas por sector)
4. Clientes en riesgo (tabla con acciones sugeridas para cada uno)
5. Áreas de mejora priorizadas (con evidencia de los comentarios)
6. Recomendaciones concretas (3-5 acciones)

Genera también salida/clientes_en_riesgo.csv para importar en el CRM.
```

**Qué observar:**
- El NPS es una métrica estándar: el pipeline debe calcularlo correctamente.
- La identificación de clientes en riesgo combina datos numéricos con análisis de texto.
- El CSV de salida facilita la acción inmediata en el CRM.

---

## Ejercicio 3: Pipeline de preparación de propuesta comercial

**Prerequisitos:** Documentos del cliente potencial y datos financieros internos. Claude Code instalado.

**Contexto:** Preparar una propuesta comercial requiere recopilar información dispersa, preparar números, redactar un documento coherente y verificar que todo cuadra. Este pipeline estructura el proceso en cuatro fases para que nada se quede atrás.

### Paso A — Preparar la estructura

```
propuesta-comercial/
├── cliente/
│   ├── briefing_cliente.md          ← necesidades expresadas por el cliente
│   ├── reunion_notas.md             ← notas de la reunión de toma de requisitos
│   └── requisitos_tecnicos.pdf      ← documento técnico del cliente (si existe)
├── interno/
│   ├── catalogo_servicios.csv       ← columnas: Servicio, Descripcion, PrecioBase, UnidadMedida
│   ├── casos_exito.md               ← casos de éxito relevantes por sector
│   └── margenes_referencia.csv      ← columnas: TipoServicio, MargenMinimo, MargenObjetivo
├── salida/
└── CLAUDE.md
```

### Paso B — El prompt completo

```text
Prepara una propuesta comercial completa ejecutando estas cuatro fases.

FASE 1 — RECOPILAR Y ENTENDER
Lee todos los archivos de la carpeta cliente/:
- briefing_cliente.md
- reunion_notas.md
- requisitos_tecnicos.pdf (si existe)

Extrae y estructura:
- Nombre del cliente y sector.
- Problema o necesidad principal.
- Requisitos funcionales (qué necesitan).
- Requisitos técnicos (restricciones, integraciones, plazos).
- Criterios de decisión mencionados (precio, plazo, experiencia, etc.).
- Preguntas sin resolver o ambigüedades detectadas.

Guarda el análisis en salida/01_analisis_necesidades.md.

FASE 2 — PREPARAR NÚMEROS
Lee los archivos de la carpeta interno/:
- catalogo_servicios.csv
- margenes_referencia.csv

Con el análisis de la Fase 1:
1. Selecciona los servicios del catálogo que responden a las necesidades del cliente.
2. Estima las cantidades necesarias de cada servicio (horas, licencias, unidades).
3. Calcula tres escenarios de precio:
   - BÁSICO: cubre los requisitos mínimos.
   - RECOMENDADO: cubre todos los requisitos con margen de maniobra.
   - PREMIUM: incluye servicios adicionales de valor añadido.
4. Para cada escenario: detalle de servicios, cantidades, precio unitario, subtotal,
   descuento propuesto (si aplica), total sin IVA, IVA y total con IVA.
5. Verifica que los márgenes de cada servicio están dentro de los rangos
   de margenes_referencia.csv. Si alguno está por debajo del mínimo, marca con ALERTA.

Guarda la tabla de precios en salida/02_presupuesto_detallado.md.

FASE 3 — COMPONER LA PROPUESTA
Lee los casos de éxito de interno/casos_exito.md y selecciona los 2 más relevantes
para el sector del cliente.

Redacta la propuesta completa en salida/03_propuesta_NOMBRE_CLIENTE.md con estas
9 secciones:

1. PORTADA
   - Título: "Propuesta de [servicio principal] para [nombre del cliente]"
   - Fecha, referencia interna, periodo de validez (30 días).

2. RESUMEN EJECUTIVO (1 página)
   - El problema del cliente en 3-4 líneas.
   - Nuestra solución en 3-4 líneas.
   - Beneficio principal cuantificado si es posible.

3. ENTENDIMIENTO DE LA NECESIDAD
   - Demostrar que hemos comprendido el contexto del cliente.
   - Listar requisitos funcionales y técnicos identificados.

4. SOLUCIÓN PROPUESTA
   - Descripción detallada de cada servicio incluido.
   - Cómo cada servicio responde a un requisito concreto.
   - Arquitectura o diagrama de alto nivel si aplica.

5. METODOLOGÍA Y PLAN DE TRABAJO
   - Fases del proyecto con duración estimada.
   - Hitos y entregables por fase.
   - Equipo propuesto (roles, no nombres).

6. CASOS DE ÉXITO
   - Los 2 casos seleccionados, con contexto, solución y resultados.

7. INVERSIÓN
   - Los tres escenarios de precio (Básico, Recomendado, Premium).
   - Tabla comparativa clara.
   - Condiciones de pago propuestas.

8. EQUIPO Y GARANTÍAS
   - Compromiso de calidad.
   - SLAs si aplica.
   - Contacto de referencia.

9. PRÓXIMOS PASOS
   - Qué necesitamos del cliente para arrancar.
   - Plazo estimado para inicio tras aprobación.

Tono profesional, orientado al valor para el cliente. Sin exageraciones.
Extensión total: 8-12 páginas.

FASE 4 — VERIFICAR
Revisa la propuesta completa y verifica:
1. Coherencia: ¿lo prometido en la solución está presupuestado?
2. Completitud: ¿todos los requisitos del cliente tienen respuesta?
3. Precios: ¿los totales cuadran? ¿los márgenes están en rango?
4. Ortografía y gramática.
5. Que no hay información placeholder ni textos genéricos sin personalizar.

Genera salida/04_checklist_verificacion.md con el resultado de cada punto:
OK o CORREGIR con detalle.

Si hay puntos a corregir, aplica las correcciones en la propuesta y vuelve a verificar.
```

**Qué observar:**
- La Fase 1 es pura comprensión: si el análisis de necesidades falla, todo lo demás estará desenfocado.
- La Fase 2 genera tres escenarios porque rara vez un presupuesto único encaja con lo que el cliente tiene en mente.
- La Fase 4 cierra el ciclo con una verificación explícita que evita enviar propuestas con errores.

---

## Preguntas de reflexión

Después de completar los ejercicios, considera:

1. **Puntos de control:** Los tres pipelines tienen fases con validación intermedia. ¿Qué ocurriría si ejecutaras todo en un solo prompt sin separar fases?
2. **Datos sensibles:** El pipeline financiero y el de propuestas manejan información confidencial. ¿Qué precauciones tomarías al usar un LLM con estos datos?
3. **Reproducibilidad:** Si ejecutas el mismo pipeline dos veces con los mismos datos, ¿obtendrás el mismo resultado? ¿Importa?
