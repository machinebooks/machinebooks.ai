# Capítulo 1 — Ya usas IA, pero no un agente

## Ejercicio 1: De pregunta a instrucción de trabajo

**Requisitos:** Cuenta en claude.ai (el plan gratuito es suficiente).

### Paso A — Enfoque chatbot

```text
¿Cómo puedo organizar mejor mis archivos de trabajo?
```

### Paso B — Enfoque agente

```text
Tengo una carpeta con 200 archivos de trabajo de todo el año 2024.
Hay PDFs, documentos Word, hojas Excel, presentaciones PowerPoint e imágenes.
No tienen un sistema de nombres coherente.

Necesito un plan de organización concreto que incluya:
1. Estructura de subcarpetas por trimestre y tipo de documento
2. Un patrón de nomenclatura para cada tipo de archivo
   (ejemplo: 2024-Q1-FACTURA-001-proveedor.pdf)
3. Una tabla con los 10 nombres actuales más caóticos como ejemplo
   y su nombre nuevo propuesto
4. Un script que yo pueda darle a un agente para que ejecute
   la reorganización completa

Sé concreto. No me des consejos generales, dame el plan ejecutable.
```

---

## Ejercicio 2: Probar la delegación con un documento real

**Requisitos:** Un documento de trabajo real (informe, acta, presupuesto, email largo). Súbelo a Claude.ai con el icono del clip.

### Paso A — Enfoque chatbot

```text
Resúmeme este documento.
```

### Paso B — Enfoque agente

```text
Analiza este documento y genera:

1. RESUMEN EJECUTIVO (3-5 líneas): para enviárselo a mi jefe,
   que no va a leer el documento completo.

2. DECISIONES PENDIENTES: lista cada decisión que este documento
   requiere, quién debería tomarla, y la fecha límite si se menciona.

3. DATOS CLAVE: extrae todas las cifras, fechas y nombres propios
   en una tabla estructurada.

4. RIESGOS: identifica cualquier riesgo, problema o incertidumbre
   mencionada en el documento.

5. PRÓXIMOS PASOS: genera la lista de acciones concretas que se
   derivan de este documento, con responsable sugerido si es posible.

Formato: usa Markdown con tablas donde corresponda.
Tono: profesional pero directo.
```

---

## Ejercicio 3: El catálogo de tareas delegables

**Requisitos:** Papel y bolígrafo (o un documento en blanco). No necesitas Claude.

Lista todas las tareas de la última semana. Clasifica cada una en tres categorías:

| Categoría | Descripción | Ejemplo |
|---|---|---|
| **Criterio humano** | Requiere tu juicio, experiencia o decisión política | Aprobar un presupuesto; negociar con un cliente |
| **Operativa repetitiva** | Sigue un patrón predecible, mismos pasos cada vez | Extraer datos de facturas; consolidar informes semanales |
| **Mixta** | Tiene una parte automatizable y otra que requiere tu juicio | Preparar una presentación (estructura automatizable, mensaje clave tuyo) |

---

## Ejercicio 4: Tu primera instrucción de trabajo real

**Requisitos:** Ninguno. Este es un ejercicio de escritura — NO lo envíes a Claude todavía.

Piensa en la tarea operativa más tediosa que tengas pendiente esta semana. Escribe una instrucción de trabajo con esta plantilla:

```text
TAREA: [Qué necesito que se haga]
DATOS DE ENTRADA: [Dónde están los datos, en qué formato]
RESULTADO ESPERADO: [Qué quiero obtener, en qué formato]
CRITERIOS: [Reglas que debe seguir]
RESTRICCIONES: [Qué NO debe hacer]
CONTEXTO: [Información adicional que necesita saber]
```

**Ejemplo:**

```text
TAREA: Consolidar las ventas del trimestre por región
DATOS DE ENTRADA: 3 archivos Excel en la carpeta /ventas/, uno por mes
RESULTADO ESPERADO: Un único archivo Excel con totales por región y mes,
  más un resumen ejecutivo de una página en Word
CRITERIOS: Usar formato europeo de números (1.234,56 €), ordenar
  por volumen de mayor a menor
RESTRICCIONES: No modificar los archivos originales
CONTEXTO: Las regiones son Norte, Sur, Este, Oeste y Canarias.
  "Canarias" a veces aparece como "Islas Canarias" en los datos.
```
