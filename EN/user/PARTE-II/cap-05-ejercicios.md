# Capítulo 5 — Del PDF al dato: extraer información de documentos

Ejercicios prácticos con prompts listos para copiar y pegar en Claude Code o Claude Desktop.

---

## Caso 1: Extraer datos de 50 facturas a CSV

**Prerequisitos:** Una carpeta con facturas en formato PDF. Adapta la ruta y los campos a tu caso real.

**Contexto:** Extraer datos de facturas manualmente es una de las tareas que mas tiempo consume en administracion. Este prompt define campos concretos, formato de salida y reglas para datos ilegibles, evitando que el agente invente informacion.

```text
Tengo 50 facturas PDF en la carpeta C:\Users\miusuario\Documents\Facturas_Q1_2024.

Necesito que extraigas de cada una los siguientes campos:
- Nombre del proveedor
- NIF del proveedor
- Número de factura
- Fecha de emisión
- Concepto(s)
- Base imponible
- Tipo de IVA (%)
- Importe de IVA
- Total factura
- Forma de pago (si aparece)

Genera un archivo CSV con todos los datos, una fila por factura.
Añade una columna "Nombre_archivo_original" para saber de qué PDF viene cada dato.
Si no puedes leer algún campo, pon "NO LEGIBLE" en vez de inventar.
Al final, muéstrame un resumen: total facturas procesadas, total importe,
y lista de facturas donde algún campo no se pudo extraer.
```

---

## Caso 2: Extraer cláusulas clave de 15 contratos

**Prerequisitos:** Una carpeta con contratos de proveedores en formato PDF. Adapta la ruta y los campos a los datos que necesites controlar.

**Contexto:** Revisar contratos para identificar fechas de vencimiento, cláusulas de renovación y penalizaciones es un trabajo tedioso pero crítico. Este prompt estructura la extracción para que el resultado sea directamente accionable.

```text
En la carpeta D:\Legal\Contratos_Proveedores hay 15 contratos en PDF.

Necesito una tabla con estos campos para cada contrato:
- Nombre del proveedor
- Fecha de inicio del contrato
- Fecha de vencimiento
- Importe anual o total del contrato
- Plazo de preaviso para no renovación (en días)
- ¿Tiene renovación automática? (Sí/No)
- Cláusula de penalización por cancelación anticipada (resumen en 1 línea)
- Página donde encontraste cada dato clave

Genera un CSV y ordénalo por fecha de vencimiento (el más próximo primero).
Si un dato no aparece explícitamente en el contrato, indica "No especificado".
```

---

## Caso 3: Procesar albaranes y cruzar con pedidos

**Prerequisitos:** Una carpeta con albaranes escaneados en PDF y un archivo Excel con los pedidos del mismo periodo. Adapta las rutas a tu entorno.

**Contexto:** El cruce entre lo pedido y lo recibido es una tarea habitual en almacenes y departamentos de compras. Este prompt combina dos capacidades del agente: extraer datos de PDFs escaneados y cruzarlos con una fuente de datos estructurada.

```text
Tengo dos fuentes de datos:
1. Carpeta con 30 albaranes escaneados en PDF: D:\Almacen\Albaranes_Marzo
2. Un Excel con los pedidos del mes: D:\Almacen\Pedidos_Marzo.xlsx

Para cada albarán, extrae:
- Número de albarán
- Proveedor
- Fecha de entrega
- Lista de artículos con cantidad recibida

Después, cruza con los pedidos del Excel y genera un informe de discrepancias:
- Artículos pedidos pero no recibidos
- Artículos recibidos con cantidad diferente a la pedida
- Artículos recibidos sin pedido correspondiente

Genera dos archivos:
1. albaranes_extraidos.csv con todos los datos de los albaranes
2. discrepancias_marzo.csv con solo las diferencias encontradas
```
