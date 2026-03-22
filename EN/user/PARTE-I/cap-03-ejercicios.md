# Capítulo 3 — Anatomía de un agente

## Ejercicio: El mismo problema, tres niveles de autonomía

**Requisitos:** Claude Code instalado.

### Preparación — Crea la carpeta de prueba

```text
Crea una carpeta llamada "prueba-autonomia" con 20 archivos de ejemplo:
- 5 archivos .txt con contenido simulado de informes (informe-enero.txt,
  informe-febrero.txt, etc.)
- 3 archivos .csv con datos simulados de ventas
- 4 archivos que parezcan duplicados (informe-v1.txt, informe-v2.txt,
  informe-final.txt, informe-final-revisado.txt)
- 3 archivos con nombres caóticos (asdfg.txt, copia(1).txt, sin-titulo.txt)
- 5 archivos variados (.md, .log, .bak, .tmp, .old)

Pon contenido realista en cada uno. No dejes ninguno vacío.
```

Después haz `cd prueba-autonomia`.

### Nivel 1 — Asistido (sesión interactiva)

```text
Quiero un inventario completo de esta carpeta. Antes de hacer cualquier cosa,
muéstrame tu plan paso a paso y espera mi aprobación en cada paso.
Necesito:
1. Lista de todos los archivos con tipo y tamaño
2. Identificación de posibles duplicados
3. Clasificación en: útiles, posibles duplicados, candidatos a borrar
4. Informe final guardado como inventario.md
```

### Nivel 2 — Semiautónomo (nueva sesión, misma carpeta)

```text
Genera un inventario completo de esta carpeta y guárdalo como
inventario-semi.md. Incluye: lista de archivos con tipo y tamaño,
identificación de duplicados, y clasificación en útiles, duplicados
y candidatos a borrar.

Puedes leer todos los archivos y crear el informe sin preguntarme.
No modifiques ni borres ningún archivo original.
```

### Nivel 3 — Autónomo (desde el terminal, fuera de Claude Code)

```bash
claude -p "Genera un inventario completo de los archivos de este directorio. Incluye: lista con tipo y tamaño, identificación de duplicados, clasificación (útiles, duplicados, candidatos a borrar) y recomendaciones de limpieza. Guarda el resultado como inventario-auto.md. No modifiques ni borres archivos originales."
```

> Compara los tres archivos resultantes y anota el tiempo total de cada nivel.

---

## Ejercicio: Construye tu archivo CLAUDE.md

**Requisitos:** Claude Code. Una carpeta de trabajo real.

```text
Quiero crear un archivo CLAUDE.md para esta carpeta que le dé contexto
a cualquier agente que trabaje aquí. Primero, analiza el contenido del
directorio para entender qué tipo de trabajo se hace aquí. Después,
genera un CLAUDE.md con:

1. Descripción breve de qué contiene esta carpeta
2. Estructura de subcarpetas y qué hay en cada una
3. Convenciones de nomenclatura que observes en los archivos existentes
4. Formatos preferidos para documentos nuevos (basándote en los que ya existen)
5. Cualquier instrucción útil que debería saber un agente que trabaje aquí

Sé concreto y práctico. Este archivo lo leerá el agente cada vez que
trabaje en esta carpeta.
```

**Plantilla de referencia:**

```text
# Contexto del proyecto

Este directorio contiene [descripción].

## Estructura
- /informes/ — Informes mensuales de estado (formato: informe-YYYY-MM.md)
- /datos/ — Hojas de cálculo de seguimiento
- /presentaciones/ — Decks para reuniones de seguimiento

## Convenciones
- Fechas: formato YYYY-MM-DD
- Importes: euros con formato europeo (1.234,56 €)
- Idioma: español de España
- Documentos nuevos: siempre en Markdown salvo que se indique otro formato

## Instrucciones para el agente
- Cuando generes informes, usa la plantilla de /plantillas/
- No borres nunca archivos sin preguntar
- Si encuentras datos inconsistentes, señálalos en lugar de asumirlos
```
