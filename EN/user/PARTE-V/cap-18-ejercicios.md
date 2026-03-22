# Capítulo 18 — Visualización instantánea: de datos a gráficos con un prompt

Ejercicio guiado en 5 pasos con prompts listos para copiar y pegar en Claude Code o Claude Desktop. El caso completo parte de un CSV de KPIs y llega hasta un dashboard completo y un script reutilizable.

---

## Preparacion: Generar datos de prueba

**Contexto:** Si no tienes datos reales de KPIs, este prompt genera un CSV con metricas mensuales realistas de una empresa de servicios, incluyendo tendencias y estacionalidad para que los graficos sean interesantes.

```text
Genera un fichero kpis-2024.csv con métricas mensuales de una empresa de
servicios tecnológicos (enero 2023 a diciembre 2024, 24 meses).

Columnas:
- mes (formato YYYY-MM)
- ingresos (entre 180.000€ y 350.000€, con tendencia creciente y
  estacionalidad: caída en agosto, pico en noviembre-diciembre)
- gastos (entre 150.000€ y 280.000€, crecimiento más lento que ingresos)
- beneficio (ingresos - gastos)
- margen_pct (beneficio / ingresos * 100)
- clientes_activos (entre 35 y 75, crecimiento progresivo)
- clientes_nuevos (entre 2 y 8 por mes)
- clientes_perdidos (entre 0 y 3 por mes)
- pedidos_nuevos (entre 15 y 45)
- pedidos_entregados (entre 12 y 40)
- ticket_medio (ingresos / pedidos_entregados)
- horas_facturables (entre 2.800 y 5.200)
- tasa_ocupacion (horas_facturables / horas_disponibles * 100,
  entre 65% y 92%)
- nps (entre 25 y 65, con mejora gradual)
- satisfaccion_media (entre 6.5 y 8.8, escala 1-10)
- tasa_conversion (entre 28% y 52%)
- tiempo_medio_entrega_dias (entre 18 y 45)

Haz que los datos sean coherentes entre sí y con tendencias realistas.
El segundo año debe ser mejor que el primero en la mayoría de métricas.
Guárdalo en la carpeta actual.
```

---

## Paso 1 — Grafico rapido y refinamiento iterativo

**Objetivo:** Crear un primer grafico simple y luego mejorarlo paso a paso. Este flujo iterativo es la forma mas natural de trabajar con visualizaciones: nunca sale perfecto a la primera.

### 1.1 — Primer grafico

```text
Lee el fichero kpis-2024.csv y genera un gráfico de líneas con la evolución
mensual de ingresos, gastos y beneficio (las tres líneas en el mismo gráfico).

Eje X: meses (formato "Ene 23", "Feb 23", etc.)
Eje Y: euros (con formato 200K, 300K, etc.)
Título: "Evolución financiera mensual (2023-2024)"

Guárdalo como evolucion-financiera.png a 150 DPI.
```

### 1.2 — Refinar el grafico

```text
El gráfico está bien pero necesita ajustes:

1. Añade una zona sombreada entre ingresos y gastos que represente
   el beneficio visualmente (verde si positivo, rojo si negativo)
2. Marca con una línea vertical punteada la separación entre 2023 y 2024
3. Añade etiquetas solo en los valores máximo y mínimo de cada serie
4. Leyenda en la parte inferior, horizontal, sin marco
5. Fuente más grande para los ejes (12pt) y el título (16pt)
6. Cambia los colores: ingresos en azul (#2563EB), gastos en gris (#6B7280),
   beneficio en verde (#059669)

Guárdalo como evolucion-financiera-v2.png a 200 DPI.
```

### 1.3 — Version final

```text
Último ajuste al gráfico de evolución financiera:

1. Añade una segunda escala en el eje Y derecho para el margen (%)
2. Dibuja el margen como línea punteada naranja (#F59E0B) usando el eje derecho
3. Añade una nota al pie: "Fuente: datos internos | Generado con Claude Code"
4. Fondo blanco limpio, sin grid excesivo (solo líneas horizontales suaves)

Guarda como evolucion-financiera-final.png a 300 DPI.
```

---

## Paso 2 — Cuatro graficos complementarios

**Objetivo:** Crear un conjunto de graficos que cuenten una historia completa del negocio. Cada grafico responde a una pregunta diferente.

### 2.1 — Evolucion de clientes

```text
Con los datos de kpis-2024.csv, genera un gráfico de barras apiladas
que muestre la evolución mensual de clientes:

- Barra verde: clientes nuevos
- Barra roja: clientes perdidos
- Línea superpuesta: clientes activos totales (eje Y derecho)

Título: "Captación y retención de clientes"
Muestra la tasa de retención (%) como texto sobre cada mes.

Guárdalo como clientes-evolucion.png a 200 DPI.
```

### 2.2 — Ticket medio y volumen

```text
Con kpis-2024.csv, genera un gráfico combinado:

- Barras: número de pedidos entregados por mes (eje Y izquierdo)
- Línea: ticket medio en euros (eje Y derecho)
- Resalta los meses donde ticket medio supera la media global

Título: "Volumen de pedidos y ticket medio"
Incluye una línea horizontal punteada en la media del ticket medio.

Guárdalo como ticket-medio.png a 200 DPI.
```

### 2.3 — NPS y satisfaccion

```text
Con kpis-2024.csv, genera un gráfico de área con dos métricas:

- Área azul claro: satisfacción media (escala 1-10, eje Y izquierdo)
- Línea naranja gruesa: NPS (escala -100 a 100, eje Y derecho)
- Zonas de referencia NPS: rojo (<0), amarillo (0-30), verde claro (30-50),
  verde oscuro (>50) como bandas de fondo suaves

Título: "Evolución de satisfacción y NPS"
Marca el momento donde NPS supera 50 (si lo hace) con una anotación.

Guárdalo como nps-satisfaccion.png a 200 DPI.
```

### 2.4 — Tasa de conversion y eficiencia

```text
Con kpis-2024.csv, genera un gráfico de dispersión (scatter):

- Eje X: tasa de ocupación (%)
- Eje Y: tasa de conversión (%)
- Tamaño del punto: proporcional a ingresos del mes
- Color del punto: gradiente por margen (rojo bajo → verde alto)
- Etiqueta en cada punto: abreviatura del mes ("E23", "F23", etc.)

Título: "Relación entre ocupación, conversión y rentabilidad"
Añade líneas de tendencia para 2023 (punteada) y 2024 (sólida).

Guárdalo como eficiencia-scatter.png a 200 DPI.
```

---

## Paso 3 — Dashboard completo

**Objetivo:** Combinar todos los graficos en un unico panel visual, organizando como un cuadro de mando que un director pueda consultar de un vistazo.

```text
Combina los gráficos anteriores en un dashboard único con esta disposición:

FILA 1 (4 tarjetas de KPI):
- Ingresos 2024 total (con % variación vs 2023)
- Beneficio 2024 total (con % variación vs 2023)
- Clientes activos actuales (con variación neta)
- NPS actual (con flecha de tendencia)

Cada tarjeta: fondo blanco, número grande en negrita, variación en verde
(positiva) o rojo (negativa), icono o símbolo representativo.

FILA 2 (2 gráficos, 50%-50%):
- Izquierda: Evolución financiera (ingresos, gastos, beneficio)
- Derecha: Captación y retención de clientes

FILA 3 (2 gráficos, 50%-50%):
- Izquierda: Ticket medio y volumen
- Derecha: NPS y satisfacción

Estilo general:
- Fondo gris muy claro (#F9FAFB)
- Tarjetas y gráficos con fondo blanco y sombra sutil
- Título del dashboard: "Dashboard KPIs — Cierre 2024"
- Fecha de generación en esquina inferior derecha
- Paleta de colores coherente en todo el dashboard

Genera dos versiones:
1. dashboard-2024.png a 300 DPI (para imprimir o presentar)
2. dashboard-2024.html (interactivo, con tooltips al pasar el ratón)
```

---

## Paso 4 — Personalizar estilo corporativo

**Objetivo:** Adaptar el dashboard a una identidad visual concreta, como se haria en una empresa real donde los colores y tipografias estan definidos.

```text
Aplica este estilo corporativo al dashboard:

COLORES:
- Primario: #1E3A5F (azul corporativo oscuro)
- Secundario: #4A90D9 (azul medio)
- Acento: #F5A623 (naranja/dorado)
- Positivo: #27AE60 (verde)
- Negativo: #E74C3C (rojo)
- Fondo: #F4F6F8
- Texto: #2C3E50

TIPOGRAFÍA:
- Títulos: negrita, 18pt
- Subtítulos: seminegrita, 14pt
- Datos: regular, 12pt
- Notas: light, 9pt

LOGO: Añade el texto "ACME Corp" en la esquina superior izquierda
con el color primario, simulando un logotipo corporativo.

FORMATO:
- Bordes redondeados (8px) en tarjetas y gráficos
- Sombra sutil: 0 2px 8px rgba(0,0,0,0.08)
- Separación uniforme de 20px entre elementos

Regenera el dashboard completo con este estilo y guárdalo como:
- dashboard-corporativo.png (300 DPI)
- dashboard-corporativo.html
```

---

## Paso 5 — Script reutilizable

**Objetivo:** Convertir todo el trabajo manual en un script Python que pueda ejecutarse cada mes con datos nuevos, sin necesidad de repetir los prompts.

```text
Genera un script Python llamado generar_dashboard.py que:

1. ENTRADA: Recibe como argumento la ruta a un fichero CSV con el mismo
   formato que kpis-2024.csv (puede tener más o menos meses)

2. PROCESAMIENTO:
   - Lee el CSV con pandas
   - Calcula automáticamente: variaciones interanuales, medias móviles,
     tendencias
   - Detecta el último mes completo para usarlo como "mes actual"

3. GENERACIÓN DE GRÁFICOS (matplotlib + seaborn):
   - Evolución financiera (ingresos, gastos, beneficio, margen)
   - Captación y retención de clientes
   - Ticket medio y volumen
   - NPS y satisfacción
   - Scatter de eficiencia

4. DASHBOARD:
   - Compone todo en un único PNG (300 DPI) con la disposición de 3 filas
   - Aplica el estilo corporativo del paso anterior
   - Incluye las 4 tarjetas de KPI calculadas automáticamente

5. SALIDA:
   - dashboard-{periodo}.png (ej: dashboard-2024-12.png)
   - dashboard-{periodo}.html (versión interactiva con plotly)
   - resumen-kpis.json (datos de las tarjetas para integrar en otros sistemas)

6. CONFIGURACIÓN:
   - Los colores corporativos deben estar en un diccionario al inicio
     del fichero, fáciles de cambiar
   - El formato del CSV esperado debe estar documentado en un comentario
   - Si faltan columnas opcionales, el script debe funcionar sin esas
     visualizaciones en vez de fallar

Incluye docstrings, comentarios explicativos y un bloque if __name__
con ejemplo de uso. El script debe funcionar con: python generar_dashboard.py kpis-2024.csv
```

---

## Ejercicios adicionales (bonus)

### Cinco diapositivas para presentacion

```text
Usando los datos de kpis-2024.csv, genera 5 imágenes PNG (una por
diapositiva) listas para insertar en una presentación, a 300 DPI
y ratio 16:9 (1920x1080 píxeles).

DIAPOSITIVA 1 — Portada
- Título: "Informe de resultados 2024"
- Subtítulo: "Comité de Dirección — Enero 2025"
- Fondo con gradiente del azul corporativo (#1E3A5F → #4A90D9)
- Texto en blanco

DIAPOSITIVA 2 — KPIs clave
- 4 tarjetas grandes con los KPIs principales:
  Ingresos, Beneficio, Clientes activos, NPS
- Cada una con valor actual, variación vs año anterior y un mini gráfico
  sparkline de evolución
- Fondo blanco

DIAPOSITIVA 3 — Evolución financiera
- Gráfico de evolución financiera (ingresos, gastos, beneficio)
- Ocupando el 75% de la diapositiva
- 3 bullet points a la derecha con los datos más relevantes

DIAPOSITIVA 4 — Clientes y satisfacción
- Dos gráficos lado a lado:
  izquierda = evolución de clientes, derecha = NPS
- Titular: "La base de clientes crece y la satisfacción mejora"

DIAPOSITIVA 5 — Conclusiones
- 5 bullet points con las conclusiones principales extraídas de los datos
- Cada conclusión respaldada por un dato concreto
- Fondo blanco con borde lateral en azul corporativo

Guarda las 5 imágenes como slide-01.png a slide-05.png.
Aplica el estilo corporativo definido anteriormente.
```
