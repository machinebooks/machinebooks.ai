# Capítulo 4 — Archivos bajo control: analizar, renombrar, organizar y transformar

Ejercicios prácticos con prompts listos para copiar y pegar en Claude Code o Claude Desktop.

---

## Caso 1: Reorganizar facturas (87 PDFs)

**Prerequisitos:** Una carpeta con facturas en formato PDF. Adapta la ruta a tu sistema.

**Contexto:** Tienes decenas de facturas acumuladas en una sola carpeta, sin orden ni nomenclatura coherente. El agente analiza cada PDF, identifica proveedor y fecha, y reorganiza todo automáticamente.

```text
Analiza la carpeta C:\Users\miusuario\Documents\Facturas_2024.
Quiero que:
1. Leas cada PDF para identificar el proveedor y la fecha de factura
2. Renombres cada archivo con el formato: YYYY-MM-DD_proveedor_factura.pdf
3. Crees subcarpetas por mes (01-Enero, 02-Febrero, etc.)
4. Muevas cada factura a su mes correspondiente
5. Me generes un resumen en CSV con: archivo original, archivo nuevo, proveedor, fecha, importe si lo encuentras

Antes de ejecutar nada, muéstrame el plan completo.
```

---

## Caso 2: Limpiar carpeta de descargas

**Prerequisitos:** Tu carpeta de Descargas con archivos acumulados. Adapta la ruta a tu sistema.

**Contexto:** La carpeta de descargas es el cajón de sastre de cualquier ordenador. Este flujo tiene dos fases: primero analizar, luego actuar. Nunca le pidas al agente que borre directamente.

### Paso 1 — Analizar antes de actuar

```text
Analiza mi carpeta de Descargas (C:\Users\miusuario\Downloads).
Clasifica todos los archivos en estas categorías:
- Documentos (PDF, Word, Excel, PowerPoint)
- Imágenes (JPG, PNG, GIF, capturas de pantalla)
- Instaladores (EXE, MSI, DMG)
- Vídeos y audio
- Archivos comprimidos (ZIP, RAR)
- Otros

Para cada categoría, dime cuántos archivos hay y cuánto espacio ocupan.
Identifica archivos duplicados.
Identifica archivos que no se han abierto en más de 6 meses.

Muéstrame el resultado antes de proponer ninguna acción.
```

### Paso 2 — Organizar con instrucciones concretas

```text
Perfecto. Haz lo siguiente:
1. Crea subcarpetas por categoría dentro de Descargas
2. Mueve cada archivo a su categoría
3. Los instaladores de más de 6 meses, muévelos a una carpeta "Para_borrar"
4. Los duplicados, deja solo la versión más reciente y mueve el resto a "Para_borrar"
5. No borres nada — solo organiza y dame el resumen final
```

---

## Caso 3: Normalizar nombres de archivos (350 ficheros)

**Prerequisitos:** Una carpeta con archivos creados por distintas personas, con nombres inconsistentes. Adapta la ruta y las reglas a tu convención.

**Contexto:** Cuando varias personas contribuyen documentos a un mismo proyecto, los nombres de archivo se convierten en un caos. Este prompt establece reglas claras y pide validación antes de aplicar cambios masivos.

```text
En la carpeta D:\Proyectos\ClienteAlfa\Documentacion hay 350 archivos
creados por distintas personas. Necesito normalizar los nombres con estas reglas:

1. Todo en minúsculas
2. Sin espacios (usar guiones)
3. Sin caracteres especiales (ñ→n, acentos eliminados)
4. Formato: YYYY-MM-DD_tipo_descripcion-breve.ext
5. Tipos válidos: acta, informe, propuesta, contrato, presupuesto, plano, foto, otro
6. Si hay versiones múltiples del mismo documento, conservar solo la más reciente
   y mover las anteriores a una carpeta "versiones-anteriores"

Primero analiza y muéstrame una tabla con los 20 primeros renombramientos propuestos
para que valide el criterio. Después aplica a todos.
```
