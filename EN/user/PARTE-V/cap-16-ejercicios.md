# Capítulo 16 — Datos financieros: presupuestos, gastos y reporting

Ejercicio guiado en 5 pasos con prompts listos para copiar y pegar en Claude Code o Claude Desktop. El caso completo cruza cuatro fuentes financieras con inconsistencias reales y genera un informe de desviaciones presupuestarias.

---

## Preparacion: Generar datos de prueba

**Contexto:** Si no tienes datos financieros reales para practicar, este prompt genera cuatro ficheros con inconsistencias intencionadas que simulan la realidad de cualquier departamento financiero: codigos que no coinciden, categorias con distinto nombre segun el sistema de origen, y cifras que no cuadran entre si.

```text
Genera 4 ficheros financieros de una empresa mediana (200 empleados) para
el ejercicio fiscal 2024. Guárdalos en una carpeta finanzas-2024/.

FICHERO 1 — presupuesto-2024.xlsx
Presupuesto anual aprobado con estas columnas:
- Código partida (formato: PRE-XXX)
- Descripción
- Categoría (Personal, Tecnología, Marketing, Operaciones, Formación,
  Infraestructura, Servicios externos, Contingencia)
- Presupuesto Q1, Q2, Q3, Q4 (en euros)
- Presupuesto anual total
- Departamento responsable
Entre 35 y 45 partidas. Total presupuesto: ~4.5M€.

FICHERO 2 — gastos-reales-2024.csv
Gastos ejecutados mes a mes con estas columnas:
- Fecha (formato DD/MM/YYYY)
- Código ERP (formato: ERP-XXXX — NO coincide directamente con los
  códigos de presupuesto, esa es la gracia)
- Concepto
- Categoría ERP (usa nombres DIFERENTES a los del presupuesto:
  "Nóminas" en vez de "Personal", "IT" en vez de "Tecnología", etc.)
- Importe (con IVA incluido en algunos casos, sin IVA en otros)
- Departamento
- Proveedor
- Estado (Pagado, Pendiente, En revisión)
Entre 800 y 1.200 registros.

FICHERO 3 — forecast-q4.xlsx
Previsión actualizada del Q4 con estas columnas:
- Código partida (formato PRE-XXX, igual que presupuesto)
- Descripción
- Estimación octubre, noviembre, diciembre
- Total Q4 estimado
- Variación respecto a presupuesto original (%)
- Comentario del responsable
Debe haber 5-8 partidas con desviación significativa (>15%).

FICHERO 4 — compromisos-pendientes.csv
Compromisos adquiridos pero no ejecutados:
- Fecha compromiso
- Proveedor
- Concepto
- Importe comprometido
- Fecha prevista de pago
- Código partida asociado (algunos con código PRE-XXX, otros con
  código ERP-XXXX, otros sin código)
- Estado (Firmado, En negociación, Pendiente aprobación)
Entre 20 y 30 registros.

INCONSISTENCIAS INTENCIONADAS:
- Los códigos de presupuesto (PRE-XXX) y los del ERP (ERP-XXXX) no tienen
  mapeo directo — hay que construirlo por descripción/categoría
- Las categorías del presupuesto y del ERP usan nombres distintos
- Algunos gastos reales no tienen partida presupuestaria obvia
- El forecast del Q4 contradice parcialmente los compromisos pendientes
- 3-4 proveedores aparecen con nombres ligeramente diferentes entre ficheros
- Algunos importes del fichero de gastos incluyen IVA y otros no (sin indicarlo)
```

---

## Paso 1 — Diagnosticar las fuentes

**Objetivo:** Antes de cruzar nada, entender que contiene cada fichero, que formato tiene y donde estan las inconsistencias que habra que resolver.

```text
Analiza los 4 ficheros de la carpeta finanzas-2024/ y genera un diagnóstico
completo:

Para cada fichero:
- Número de filas y columnas
- Tipos de datos por columna
- Rango de fechas cubierto
- Valores únicos en campos clave (categorías, departamentos, códigos)
- Campos con datos faltantes: cuántos y en qué columnas
- Formato de importes: ¿incluyen IVA? ¿tienen símbolo de moneda?

Diagnóstico cruzado:
- ¿Los códigos de partida del presupuesto aparecen en los gastos reales?
  Si no, ¿qué sistema de códigos usa cada fichero?
- ¿Las categorías son consistentes entre ficheros? Lista las variantes
  que encuentres.
- ¿Los departamentos se llaman igual en todos los ficheros?
- ¿Hay proveedores que aparezcan con nombres diferentes?

No modifiques nada. Solo diagnostica y lista los problemas que habrá
que resolver antes del cruce.
```

---

## Paso 2 — Construir el mapeo de categorias

**Objetivo:** Crear la tabla de correspondencia entre los codigos y nombres del presupuesto y los del ERP. Sin este mapeo, es imposible cruzar las fuentes.

```text
Basándote en el diagnóstico anterior, construye una tabla de mapeo entre
el presupuesto y el ERP:

TABLA 1 — Mapeo de códigos:
| Código presupuesto (PRE-XXX) | Código ERP (ERP-XXXX) | Descripción | Método de mapeo |

Para construir el mapeo:
1. Primero intenta por coincidencia exacta de descripción
2. Si no hay coincidencia exacta, busca por similitud semántica
   (ej: "Licencias software" ↔ "Renovación licencias anuales")
3. Si no hay coincidencia clara, márcalo como "Sin mapeo — revisar"

TABLA 2 — Mapeo de categorías:
| Categoría presupuesto | Categoría ERP | Confianza (alta/media/baja) |

Ejemplo esperado:
| Personal | Nóminas | Alta |
| Tecnología | IT | Alta |
| Servicios externos | Consultoría | Media |

TABLA 3 — Normalización de proveedores:
| Variante encontrada | Nombre normalizado |

Guarda las tres tablas en un fichero mapeo-financiero.xlsx para referencia.
Marca en rojo las filas con confianza baja o sin mapeo.
```

---

## Paso 3 — Cruce y conciliacion

**Objetivo:** Con el mapeo construido, cruzar los gastos reales contra el presupuesto para detectar desviaciones, gastos sin partida y partidas sin ejecucion.

```text
Usando el mapeo de mapeo-financiero.xlsx, cruza los gastos reales con el
presupuesto aprobado e incorpora los compromisos pendientes.

Ejecuta estas conciliaciones:

1. GASTOS vs PRESUPUESTO (por partida y trimestre)
   - Para cada partida presupuestaria, suma los gastos reales ejecutados
   - Calcula: presupuesto, ejecutado, diferencia, % ejecución
   - Clasifica cada partida: infraejecutada (<80%), en rango (80-110%),
     sobreejecutada (>110%)
   - Normaliza IVA: todos los importes a base imponible para comparar

2. GASTOS SIN PARTIDA
   - Lista los gastos reales que no se pudieron mapear a ninguna partida
   - Agrúpalos por categoría ERP y muestra el total
   - Sugiere a qué partida podrían pertenecer

3. PARTIDAS SIN EJECUCIÓN
   - ¿Hay partidas presupuestarias con 0€ ejecutados?
   - ¿Son partidas de Q4 pendientes o realmente sin actividad?
   - Cruza con compromisos pendientes: ¿alguna partida sin ejecución
     tiene compromisos firmados?

4. COMPROMISOS vs DISPONIBLE
   - Para cada compromiso pendiente, calcula cuánto presupuesto queda
     disponible en su partida
   - Marca los compromisos que superan el presupuesto restante
   - Lista compromisos sin partida asignada

Genera un fichero conciliacion-2024.xlsx con una hoja por cada conciliación.
Resalta en rojo las filas con problemas que requieren decisión humana.
```

---

## Paso 4 — Informe de desviaciones presupuestarias

**Objetivo:** Convertir los datos cruzados en un informe ejecutivo que un director financiero pueda usar directamente para tomar decisiones.

```text
Con los datos de la conciliación, genera un informe completo de desviaciones
presupuestarias con estas 7 secciones:

1. RESUMEN EJECUTIVO (1 página)
   - Presupuesto total aprobado vs gasto ejecutado a fecha
   - % de ejecución global
   - Presupuesto comprometido pendiente
   - Presupuesto disponible real (aprobado - ejecutado - comprometido)
   - Semáforo general: verde (ejecución <95%), amarillo (95-105%),
     rojo (>105%)

2. DESVIACIONES POR CATEGORÍA (tabla + análisis)
   - Tabla: categoría, presupuesto, ejecutado, comprometido, disponible,
     % desviación
   - Análisis narrativo de las 3 categorías con mayor desviación positiva
   - Análisis narrativo de las 3 categorías con mayor desviación negativa
   - ¿Las desviaciones se compensan entre sí o hay riesgo de sobrecoste global?

3. DESVIACIONES POR DEPARTAMENTO
   - Misma tabla pero agrupada por departamento
   - ¿Qué departamento gestiona mejor su presupuesto?
   - ¿Cuál tiene más gastos sin partida asignada?

4. EVOLUCIÓN TRIMESTRAL
   - Tabla trimestral: presupuesto Q1-Q4 vs ejecutado Q1-Q3 + forecast Q4
   - ¿La desviación se ha ido corrigiendo o empeorando trimestre a trimestre?
   - Comparar forecast Q4 vs presupuesto Q4 original

5. ANÁLISIS DE RIESGOS FINANCIEROS
   - Partidas con ejecución >100% antes de cerrar el año
   - Compromisos pendientes que superan el presupuesto disponible
   - Gastos recurrentes que crecen mes a mes
   - Concentración en proveedores: ¿algún proveedor supone >20% del gasto?

6. GASTOS EXTRAORDINARIOS
   - Operaciones individuales por encima de 10.000€
   - Gastos clasificados como "Contingencia" — ¿son realmente imprevistos?
   - Gastos que no encajan en ninguna categoría presupuestaria

7. RECOMENDACIONES
   - 3-5 acciones concretas para cerrar el año dentro del presupuesto
   - Partidas donde se puede reasignar presupuesto no utilizado
   - Proveedores con los que renegociar condiciones
   - Propuestas para mejorar el proceso de control presupuestario en 2025

Genera el informe en Markdown y también como Excel
(informe-desviaciones-2024.xlsx) con cada sección en una hoja separada.
Tono profesional y directo: si hay un problema, nómbralo claramente.
```

---

## Paso 5 — Ajustar proyecciones excluyendo costes puntuales

**Objetivo:** Separar los gastos recurrentes de los puntuales para generar una proyeccion mas realista del gasto base de la empresa.

```text
Analiza los gastos ejecutados en 2024 y sepáralos en dos categorías:

GASTOS RECURRENTES:
- Nóminas, licencias software, alquileres, suministros, mantenimientos
- Gastos que aparecen todos los meses o todos los trimestres
- Servicios con contrato continuado

GASTOS PUNTUALES (one-time):
- Compras de equipamiento
- Proyectos con fecha de inicio y fin
- Gastos de contingencia
- Cualquier gasto que no se espera que se repita en 2025

Con esta separación:

1. Calcula el gasto base mensual recurrente (media de los 12 meses,
   excluyendo puntuales)
2. Calcula la tendencia del gasto recurrente: ¿crece, decrece o es estable?
3. Proyecta el gasto recurrente para 2025 (12 meses) aplicando la tendencia
4. Lista los gastos puntuales previsibles para 2025 (renovaciones,
   vencimientos de contrato del fichero de compromisos)
5. Genera una propuesta de presupuesto 2025 = gasto recurrente proyectado
   + puntuales previstos + 5% de contingencia

Presenta el resultado como una tabla con:
| Categoría | Recurrente 2024 | Tendencia | Proyección 2025 | Puntuales previstos | Total 2025 |

Incluye una nota explicativa de la metodología utilizada y las limitaciones
de la proyección (qué factores no estás considerando).
```
