# Capítulo 7 — Presentaciones con estructura

Ejercicios prácticos con prompts listos para copiar y pegar en Claude Code o Claude Desktop.

---

## Caso 1: Presentación de resultados trimestrales (15 slides)

**Prerequisitos:** Tres archivos con datos del trimestre: un informe de cierre en Markdown, un Excel con datos de ventas y un archivo de texto con notas. Adapta las rutas a tu entorno.

**Contexto:** Preparar una presentacion para el comite de direccion requiere sintesis, estructura y mensajes claros. Este prompt define la audiencia, el tiempo disponible y la estructura slide por slide, para que el agente genere contenido directamente presentable.

```text
Necesito una presentación de resultados del Q1 2024 para el comité
de dirección. Máximo 20 minutos (15 presentación + 5 preguntas).

Fuentes:
1. Informe de cierre: C:\Informes\Q1\informe_cierre_Q1_2024.md
2. Ventas: C:\Informes\Q1\ventas_Q1_2024.xlsx
3. Notas: C:\Informes\Q1\notas_trimestre.txt

Audiencia: CEO, CFO, Director Comercial, Directora de Operaciones.

Estructura (15 slides):
- Portada + Resumen ejecutivo (KPIs con semáforo)
- Resultados financieros (3 slides)
- Análisis comercial (3 slides)
- Proyectos y satisfacción (2 slides)
- Riesgos y oportunidades (2 slides)
- Plan Q2 + Cierre con pregunta para la discusión

Por cada slide: título (max 8 palabras), contenido (max 5 puntos),
notas del presentador (3-5 frases), sugerencia visual.
Formato: Markdown + versión HTML de emergencia.
```

---

## Caso 2: La técnica del esqueleto — pide la estructura primero

**Prerequisitos:** Los archivos de datos que alimentarán la presentación. Este prompt es genérico y se adapta a cualquier caso.

**Contexto:** Pedirle al agente que genere directamente 30 slides suele producir resultados mediocres. La técnica del esqueleto consiste en pedir primero la estructura y validarla antes de generar el contenido. Esto te da control sobre el mensaje sin tener que rehacer todo.

```text
Tengo que hacer una presentación de 30 minutos sobre los resultados
del primer semestre para el consejo de administración. Los datos están
en estos archivos: [rutas].

No generes la presentación todavía. Primero propónme:
1. Número de diapositivas recomendado
2. Estructura (título de cada slide y contenido previsto)
3. Los 3 mensajes clave que debería transmitir
4. Qué datos incluir y cuáles dejar para el anexo
5. Posible pregunta difícil que me harán y cómo prepararme

Después de validar la estructura, generamos las slides.
```
