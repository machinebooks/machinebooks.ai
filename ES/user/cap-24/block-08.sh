# Extraído de: LibroUsuario/cap-24-pipelines-de-datos.md
cd /home/usuario/reporting-mensual

claude -p "
PIPELINE DE REPORTING FINANCIERO - ENERO 2025

Ejecuta el siguiente pipeline completo:

=== FASE 1: OBTENER Y VALIDAR DATOS ===
1. Lee todos los archivos CSV de la carpeta datos/
2. Para cada archivo, verifica:
   - Que no está vacío
   - Que las columnas esperadas están presentes
   - Que los importes son numéricos válidos
   - Que las fechas son de enero 2025
3. Si algún archivo tiene problemas, documéntalos pero continúa con los datos válidos
4. Genera un log de validación en informes/validacion-enero.md

=== FASE 2: LIMPIAR Y PREPARAR ===
1. De facturacion-enero.csv:
   - Filtra solo las facturas con estado 'Emitida' (las de 'Borrador' se reportan aparte)
   - Calcula el total facturado
   - Agrupa por cliente

2. De gastos-enero.csv:
   - Separa gastos pagados de gastos pendientes
   - Agrupa por categoría
   - Calcula totales por categoría y total general

3. De cobros-enero.csv:
   - Cruza con facturacion-enero.csv para identificar facturas cobradas vs pendientes de cobro
   - Calcula el ratio de cobro (cobrado / facturado * 100)

4. De presupuesto-q1.csv:
   - Extrae solo las filas de enero
   - Prepara la comparativa presupuesto vs. real

=== FASE 3: ANALIZAR ===
1. Calcula indicadores clave:
   - Total facturado (solo facturas emitidas)
   - Total cobrado
   - Ratio de cobro
   - Total gastos pagados
   - Total gastos comprometidos (pendientes)
   - Margen operativo (facturado - gastos pagados)
   - Desviación vs. presupuesto por categoría

2. Identifica:
   - El cliente con mayor facturación
   - La categoría de gasto con mayor desviación vs. presupuesto
   - Facturas emitidas pero no cobradas (riesgo de morosidad)
   - Gastos pendientes de pago que afectan a tesorería

3. Compara con el presupuesto:
   - ¿Estamos por encima o por debajo en ingresos?
   - ¿Estamos por encima o por debajo en gastos?
   - ¿Cuál es la desviación neta?

=== FASE 4: GENERAR INFORME ===
Genera el archivo informes/informe-financiero-enero-2025.md con esta estructura:

# Informe financiero mensual — Enero 2025

## Resumen ejecutivo
[3-5 líneas con los hallazgos principales]

## Indicadores clave
[Tabla con los KPIs calculados]

## Ingresos
### Facturación emitida
[Tabla por cliente con importes]
### Estado de cobros
[Tabla de facturas cobradas vs. pendientes]
### Facturas en borrador (no incluidas en el total)
[Lista informativa]

## Gastos
### Por categoría
[Tabla con gastos pagados y pendientes por categoría]
### Detalle de gastos pendientes de pago
[Lista para seguimiento de tesorería]

## Comparativa con presupuesto
[Tabla: categoría | presupuesto | real | desviación | % desviación]

## Conclusiones y recomendaciones
[3-5 puntos accionables basados en los datos]

## Anexo: Log de validación de datos
[Resumen de la validación de la fase 1]

=== SI ALGO FALLA ===
- Si un archivo CSV no existe, documéntalo y continúa con los demás
- Si los datos tienen formato inesperado, intenta adaptarte y documenta la incidencia
- Si un cálculo no tiene sentido (ej: porcentaje > 100% en algo que no debería), señálalo
- En cualquier caso, genera el informe con los datos disponibles y marca las secciones afectadas
"
