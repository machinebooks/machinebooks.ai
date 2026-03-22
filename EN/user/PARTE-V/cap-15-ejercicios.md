# Capítulo 15 — Excel y CSV a tu servicio: limpiar, transformar y analizar datos

Ejercicio guiado en 5 pasos con prompts listos para copiar y pegar en Claude Code o Claude Desktop. El caso completo consolida 12 ficheros mensuales de gastos en un informe anual limpio.

---

## Ejercicio completo: Consolidar 12 ficheros mensuales de gastos

**Prerequisitos:** Una carpeta `gastos-2024/` con 12 ficheros (uno por mes) en formato CSV o Excel. Pueden tener formatos ligeramente distintos entre si (columnas con diferente nombre, formatos de fecha variados, filas duplicadas). Si no tienes datos reales, puedes pedirle al agente que genere datos de ejemplo.

**Contexto:** En muchas organizaciones, cada departamento o persona registra gastos en su propia hoja, con su propio criterio. Al final del ano, alguien tiene que juntar todo en un unico fichero coherente. Este ejercicio reproduce exactamente esa situacion: 12 ficheros con inconsistencias reales que hay que detectar, limpiar y consolidar antes de analizar.

---

### Paso 1 — Explorar antes de tocar nada

**Objetivo:** Entender que hay en cada fichero antes de modificar nada. Este paso es critico porque te evita sorpresas en los pasos siguientes.

```text
Analiza todos los ficheros de la carpeta gastos-2024/. Para cada uno, dime:
cuántas filas tiene, qué columnas contiene, qué formato de fecha usa y si
detectas problemas obvios (celdas vacías, duplicados, formatos inconsistentes).
No modifiques nada todavía.
```

**Que esperar:** El agente te mostrara una tabla resumen con el nombre de cada fichero, numero de filas, lista de columnas y problemas detectados. Revisa esta tabla con atencion antes de pasar al siguiente paso. Si algun fichero tiene una estructura completamente diferente, es mejor saberlo ahora.

---

### Paso 2 — Limpiar y normalizar con reglas explicitas

**Objetivo:** Aplicar 11 reglas de limpieza concretas para que los 12 ficheros tengan la misma estructura y los mismos criterios. Las reglas son explicitas para que el agente no tome decisiones por su cuenta.

```text
Ahora limpia y normaliza los 12 ficheros aplicando estas reglas exactas:

1. COLUMNAS: Mapea todas las variantes al esquema unificado:
   - "Fecha" / "fecha_gasto" / "Date" → fecha
   - "Concepto" / "Descripcion" / "Detalle" → concepto
   - "Importe" / "Monto" / "Amount" / "Total" → importe
   - "Categoria" / "Tipo" / "Category" → categoria
   - "Departamento" / "Dept" / "Area" → departamento
   - "Proveedor" / "Supplier" / "Vendor" → proveedor

2. FECHAS: Convierte todo al formato YYYY-MM-DD. Si encuentras formatos
   como DD/MM/YYYY, MM-DD-YYYY o "15 de marzo de 2024", normalízalos.

3. IMPORTES: Todos en formato numérico con 2 decimales, sin símbolo de
   moneda, sin separador de miles. Si hay importes negativos, márcalos
   en una columna aparte "tipo_movimiento" (gasto / abono).

4. IVA: Si algún fichero incluye IVA desglosado, mantenlo. Si solo tiene
   el total, calcula base imponible e IVA al 21% y añade columnas:
   base_imponible, iva, total_con_iva.

5. CATEGORÍAS: Normaliza a estas categorías estándar:
   - Material oficina, Software/licencias, Viajes, Dietas,
     Formación, Servicios externos, Infraestructura, Marketing, Otros.
   Si encuentras variantes ("viaje", "Viajes", "VIAJES", "travel"),
   unifícalas. Las que no encajen, clasifícalas en "Otros".

6. DUPLICADOS: Identifica filas duplicadas (misma fecha + mismo importe
   + mismo proveedor). No las borres todavía, márcalas en una columna
   "posible_duplicado" (sí/no) para revisión manual.

7. FILAS VACÍAS: Elimina filas completamente vacías. Las filas con algún
   campo vacío pero datos parciales, márcalas como "incompleta".

8. ESPACIOS: Elimina espacios al inicio y final de todos los campos de texto.
   Normaliza mayúsculas: primera letra en mayúscula para categorías y
   departamentos, el resto en minúsculas.

9. PROVEEDOR: Si el campo proveedor está vacío, pon "No especificado".
   Normaliza variantes del mismo proveedor ("Amazon", "AMAZON",
   "Amazon.es" → "Amazon").

10. DEPARTAMENTO: Si falta, intenta inferirlo de la categoría
    (ej: "Marketing" → departamento Marketing). Si no es posible,
    pon "Sin asignar".

11. VALIDACIÓN FINAL: Tras aplicar todas las reglas, genera un informe
    de limpieza con: filas originales totales, filas tras limpieza,
    duplicados marcados, filas incompletas, campos corregidos por regla.

Guarda el resultado consolidado como gastos-2024-consolidado.csv.
```

**Que esperar:** Un unico fichero CSV limpio con todas las columnas normalizadas, mas un informe de limpieza que detalla exactamente que se ha cambiado. El informe es tu auditoria: si algo no cuadra, sabras donde buscar.

---

### Paso 3 — Validar la consolidacion

**Objetivo:** Verificar que el fichero consolidado es correcto antes de analizarlo.

```text
Antes de seguir, valida el fichero gastos-2024-consolidado.csv:

1. ¿La suma de filas de los 12 ficheros originales coincide con el
   consolidado (descontando filas vacías eliminadas)?
2. ¿Los totales de importe por mes cuadran con los ficheros originales?
3. ¿Hay alguna categoría con menos de 3 registros? (podría indicar
   un problema de mapeo).
4. ¿Todos los meses tienen datos? ¿Algún mes tiene significativamente
   menos filas que los demás?
5. Muéstrame las 5 filas marcadas como "posible_duplicado" para que
   yo decida si se eliminan.

Si detectas algún descuadre, dime exactamente dónde está el problema.
```

---

### Paso 4 — Analisis anual

**Objetivo:** Extraer las conclusiones de negocio que justifican todo el trabajo de limpieza. Este paso convierte datos limpios en informacion accionable.

```text
Con el fichero gastos-2024-consolidado.csv ya validado, genera un análisis
anual completo con estas 6 secciones:

1. RESUMEN EJECUTIVO
   - Gasto total anual (con y sin IVA)
   - Gasto medio mensual
   - Mes con mayor gasto y mes con menor gasto
   - Variación entre el primer y segundo semestre

2. EVOLUCIÓN MENSUAL
   - Tabla mes a mes con: total gasto, número de operaciones, gasto medio
     por operación
   - Identifica tendencia: ¿el gasto crece, decrece o es estable?
   - Señala cualquier pico o caída anómala y sugiere posibles causas

3. ANÁLISIS POR CATEGORÍA
   - Tabla con cada categoría: total gastado, porcentaje del total,
     número de operaciones, importe medio
   - Top 3 categorías por volumen
   - ¿Alguna categoría creció más de un 20% respecto al semestre anterior?

4. ANÁLISIS POR DEPARTAMENTO
   - Gasto total por departamento
   - ¿Qué departamento gasta más por empleado? (si tienes el dato,
     úsalo; si no, indica que falta)
   - Departamentos con gasto creciente vs decreciente

5. ANÁLISIS DE PROVEEDORES
   - Top 10 proveedores por volumen de gasto
   - ¿Hay concentración de riesgo? (proveedor que supere el 25% del total)
   - Proveedores nuevos en el segundo semestre vs primer semestre

6. ALERTAS Y RECOMENDACIONES
   - Gastos que superan umbrales razonables (operaciones individuales
     por encima de 5.000€)
   - Patrones sospechosos: mismo importe exacto en fechas cercanas,
     gastos en fines de semana
   - 3 recomendaciones concretas para optimizar el gasto en 2025

Presenta cada sección con tablas claras y un párrafo de interpretación.
```

---

### Paso 5 — Generar Excel final multi-hoja

**Objetivo:** Producir un fichero Excel profesional con varias hojas, listo para compartir con direccion o con el equipo financiero.

```text
Genera un fichero Excel llamado informe-gastos-2024.xlsx con estas hojas:

HOJA 1 — "Datos consolidados"
- Todos los registros limpios del fichero consolidado
- Formato de tabla con filtros activos
- Columna de importe con formato moneda (€)
- Columna de fecha con formato fecha corta
- Filas marcadas como duplicado en color amarillo

HOJA 2 — "Resumen mensual"
- Tabla pivote: filas = meses, columnas = categorías, valores = suma de importes
- Fila de totales al final
- Columna adicional con total mensual

HOJA 3 — "Por departamento"
- Una tabla por departamento con: categoría, total gastado, % del departamento
- Ordenado de mayor a menor gasto

HOJA 4 — "Top proveedores"
- Top 20 proveedores con: nombre, total facturado, número de facturas,
  importe medio, primera y última fecha de factura

HOJA 5 — "Alertas"
- Lista de todas las filas marcadas como posible duplicado
- Lista de filas incompletas
- Lista de operaciones por encima de 5.000€
- Lista de gastos en fin de semana

Aplica formato profesional: cabeceras en negrita con fondo azul oscuro
y texto blanco, bordes finos, ancho de columna ajustado al contenido.
```

---

## Ejercicios adicionales (bonus)

### Comparar dos versiones de un fichero

**Contexto:** Te han enviado una version actualizada de un presupuesto y necesitas saber que ha cambiado respecto a la version anterior.

```text
Compara estos dos ficheros:
- gastos-2024/presupuesto_v1.xlsx
- gastos-2024/presupuesto_v2.xlsx

Muéstrame exactamente qué ha cambiado:
- Filas añadidas en v2 que no estaban en v1
- Filas eliminadas en v2 que sí estaban en v1
- Celdas modificadas: valor anterior → valor nuevo
- Resumen: total de cambios por tipo (añadido/eliminado/modificado)

Genera un fichero comparativa.xlsx con los cambios resaltados en colores:
verde = añadido, rojo = eliminado, amarillo = modificado.
```

---

### Dividir un fichero grande por criterio

**Contexto:** Tienes un fichero consolidado y necesitas generar un fichero separado para cada departamento, por ejemplo para enviar a cada responsable solo sus datos.

```text
Toma el fichero gastos-2024-consolidado.csv y divídelo en ficheros separados,
uno por departamento.

Para cada departamento genera:
- Un fichero CSV: gastos-2024-{departamento}.csv
- Solo las filas de ese departamento
- Ordenadas por fecha
- Con una fila final de totales

Además, genera un fichero índice (indice-departamentos.csv) con:
nombre del departamento, número de registros, gasto total, nombre del fichero generado.

Guarda todo en una carpeta gastos-por-departamento/.
```

---

### Convertir entre formatos

**Contexto:** Necesitas el mismo conjunto de datos en varios formatos porque distintos sistemas o personas lo necesitan de formas diferentes.

```text
Toma el fichero gastos-2024-consolidado.csv y genera estas versiones:

1. gastos-2024.xlsx — Excel con formato de tabla y filtros
2. gastos-2024.json — JSON con array de objetos, un objeto por fila
3. gastos-2024.parquet — Parquet para análisis en Python/pandas
4. gastos-2024-resumen.md — Tabla Markdown con el resumen mensual

Para cada conversión, confirma que el número de filas es idéntico al original.
```

---

### Generar datos de prueba

**Contexto:** No tienes 12 ficheros reales de gastos pero quieres practicar el ejercicio completo. Este prompt genera datos realistas con las inconsistencias intencionadas que hacen interesante la limpieza.

```text
Genera 12 ficheros CSV simulando gastos mensuales de una empresa de 50
empleados durante 2024 (enero a diciembre). Guárdalos en una carpeta
gastos-2024/.

Requisitos para que sean realistas:
- Entre 80 y 150 registros por mes
- 6 departamentos: Tecnología, Marketing, Ventas, RRHH, Operaciones, Dirección
- Categorías variadas: material oficina, software, viajes, dietas, formación,
  servicios externos, infraestructura, marketing
- Importes entre 5€ y 15.000€ (la mayoría entre 20€ y 500€)
- 15-20 proveedores recurrentes más algunos puntuales

Introduce estos problemas intencionadamente:
- 3 ficheros con columnas en diferente orden
- 2 ficheros con nombres de columna en inglés
- Formatos de fecha mezclados: DD/MM/YYYY en unos, YYYY-MM-DD en otros
- Algunos importes con símbolo € y otros sin él
- 10-15 filas duplicadas repartidas entre varios meses
- 8-10 filas con campos vacíos (proveedor o categoría)
- Variantes del mismo proveedor ("Amazon", "AMAZON", "Amazon.es")
- Un mes con significativamente más gastos (simulando fin de año)

Así podré practicar todo el flujo de limpieza y consolidación.
```
