# Capítulo 6 — Informes que se escriben solos

Ejercicios prácticos con prompts listos para copiar y pegar en Claude Code o Claude Desktop.

---

## Caso 1: Informe de ventas desde CSV

**Prerequisitos:** Dos archivos CSV con datos de ventas (marzo y febrero del mismo año). Las columnas esperadas son: Fecha, Cliente, Producto, Region, Importe, Estado. Adapta las rutas y columnas a tus datos reales.

**Contexto:** Generar un informe ejecutivo a partir de datos en bruto es una tarea recurrente. Este prompt define la estructura completa del informe, el tono y el formato de salida, para que el resultado sea presentable sin retoques.

```text
Lee el archivo C:\Users\miusuario\Documents\ventas_marzo_2024.csv

El archivo tiene estas columnas: Fecha, Cliente, Producto, Región,
Importe, Estado.

Genera un informe ejecutivo de ventas de marzo 2024 con esta estructura:

1. RESUMEN EJECUTIVO (5-8 líneas)
   - Ventas totales del mes
   - Comparativa con febrero (archivo: ventas_febrero_2024.csv, misma carpeta)
   - Variación porcentual
   - Dato más destacable del mes

2. ANÁLISIS POR REGIÓN (tabla + gráfico de barras)
   - Ventas por región
   - Porcentaje sobre el total
   - Variación respecto a febrero

3. TOP 10 CLIENTES (tabla)
   - Nombre, importe total, número de operaciones
   - Marca con * los que son nuevos respecto a febrero

4. ANÁLISIS POR PRODUCTO (tabla + gráfico circular)
   - Ventas por categoría de producto
   - Porcentaje del total

5. OPERACIONES EN ESTADO PENDIENTE
   - Número y valor de operaciones no cerradas
   - Antigüedad media

6. CONCLUSIONES Y RECOMENDACIONES (3-5 puntos)
   - Tendencias identificadas
   - Riesgos detectados
   - Acciones sugeridas para abril

Genera el informe en formato Markdown con los gráficos como imágenes PNG.
Tono profesional pero directo. Si algún dato es negativo, dilo claramente.
Guarda todo en C:\Users\miusuario\Documents\Informes\informe_ventas_marzo_2024\
```

---

## Caso 2: Informe semanal de estado de proyecto

**Prerequisitos:** Tres archivos del proyecto: un archivo de texto con notas de la semana, un Excel con el seguimiento de tareas y un CSV con incidencias. Adapta las rutas y la estructura a tu metodología de seguimiento.

**Contexto:** El informe semanal de estado es uno de los documentos mas repetitivos en gestion de proyectos. Este prompt usa tres fuentes de datos distintas y pide al agente que determine el estado del semaforo a partir de los datos, no de una valoracion subjetiva.

```text
Necesito generar el informe semanal de estado del proyecto "Migración ERP"
para la semana del 18 al 22 de marzo de 2024.

Fuentes de datos:
1. Notas de la semana: C:\Proyectos\MigracionERP\notas_semana_12.txt
2. Seguimiento de tareas: C:\Proyectos\MigracionERP\seguimiento_tareas.xlsx
3. Resumen de incidencias: C:\Proyectos\MigracionERP\incidencias_marzo.csv

Estructura del informe:

CABECERA
- Proyecto: Migración ERP
- Periodo: 18-22 marzo 2024
- Estado general: [Verde/Amarillo/Rojo] — decide tú según los datos

RESUMEN EJECUTIVO (3-4 líneas)

ACTIVIDADES COMPLETADAS ESTA SEMANA
ACTIVIDADES EN CURSO
ACTIVIDADES RETRASADAS
INCIDENCIAS ABIERTAS
RIESGOS IDENTIFICADOS
PLAN PARA LA PRÓXIMA SEMANA

Tono directo y factual. Sin adornos. Si hay problemas, que se vean claros.
Genera en Markdown y en HTML.
```
