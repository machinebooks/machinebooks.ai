# Capítulo 2 — Tu primer agente

## Paso 1: Configura Claude.ai (5 min)

Crea una cuenta en claude.ai. En la barra lateral, crea un proyecto llamado "Pruebas Libro Usuario". Configura estas instrucciones personalizadas:

```text
Soy un profesional que está aprendiendo a usar agentes de IA.
Cuando me expliques algo, usa lenguaje claro y evita jerga técnica.
Si necesitas usar un término técnico, explícalo brevemente.
Responde siempre en español de España.
Formatea las respuestas con Markdown: títulos, listas y tablas cuando sea apropiado.
```

Abre una conversación dentro del proyecto y escribe:

```text
¿Qué puedo hacer contigo que no podría hacer con una búsqueda en Google?
Dame 5 ejemplos concretos con una estimación de tiempo ahorrado en cada uno.
```

---

## Paso 2: Instala Claude Code (15 min)

1. Instala Node.js desde nodejs.org (versión LTS). Verifica con `node --version`.
2. Instala Claude Code:

```bash
npm install -g @anthropic-ai/claude-code
```

3. Verifica con `claude --version`.
4. Ejecuta `claude` en el terminal y autoriza en el navegador.
5. Primera prueba:

```text
¿En qué directorio estoy ahora mismo? Lista los archivos que hay aquí.
```

---

## Paso 3: Instala la extensión de VS Code (5 min)

Busca "Claude Code" en el marketplace de VS Code (publisher: Anthropic). Abre cualquier carpeta, abre el panel de Claude Code y escribe:

```text
¿Qué archivos hay en esta carpeta? Descríbeme brevemente qué contiene cada uno.
```

---

## Paso 4: Tu primer flujo real (10 min)

**Requisitos:** Claude Code instalado. Una carpeta con al menos 20 archivos (por ejemplo, tu carpeta de Descargas).

Navega a la carpeta en el terminal, inicia `claude` y pega:

```text
Analiza todos los archivos de este directorio y genera un informe de inventario
con la siguiente información:

1. RESUMEN GENERAL: número total de archivos, tamaño total,
   rango de fechas (más antiguo y más reciente).

2. DISTRIBUCIÓN POR TIPO: tabla con cada extensión de archivo (.pdf, .docx,
   .xlsx, etc.), cuántos archivos hay de cada tipo y el tamaño total por tipo.

3. ARCHIVOS MÁS GRANDES: los 10 archivos que más espacio ocupan,
   con nombre, tamaño y fecha.

4. POSIBLES DUPLICADOS: si encuentras archivos con nombres muy similares
   o el mismo tamaño exacto, señálalos como posibles duplicados.

5. RECOMENDACIONES: sugiere qué archivos podrían borrarse (temporales,
   descargas antiguas) y cómo podría organizarse mejor esta carpeta.

Guarda el informe en un archivo llamado "inventario-carpeta.md" en este
mismo directorio.
```

---

## Caso práctico: Inventario profesional de documentación de proyecto

```text
Necesito un inventario profesional de la documentación de este proyecto.
Analiza todos los archivos de este directorio y sus subcarpetas y genera
un documento llamado "inventario-proyecto.md" con:

## 1. Resumen ejecutivo
- Número total de documentos
- Tipos de documentos encontrados
- Rango de fechas
- Tamaño total

## 2. Inventario detallado
Una tabla con: nombre del archivo, ubicación (subcarpeta), tipo, tamaño,
última modificación, y una descripción breve del contenido basada
en el nombre del archivo.

## 3. Control de versiones
Identifica archivos que parecen ser versiones diferentes del mismo
documento (ejemplo: informe-v1.docx, informe-v2.docx, informe-final.docx).
Señala cuál parece ser la versión más reciente.

## 4. Limpieza recomendada
Lista los archivos que probablemente puedan eliminarse: temporales,
borradores obsoletos, duplicados. Estima cuánto espacio se liberaría.

## 5. Propuesta de organización
Sugiere una estructura de carpetas más limpia para este proyecto,
con una explicación de la lógica.

Formato: Markdown profesional con tablas.
Restricción: no modifiques ni borres ningún archivo. Solo genera el informe.
```

---

## Caso práctico: Resumen de múltiples documentos

```text
En este directorio hay 5 informes mensuales. Lee cada uno y genera
un documento llamado "resumen-trimestral.md" con:

1. EVOLUCIÓN: ¿cómo han cambiado los indicadores principales
   mes a mes? Identifica tendencias.

2. LOGROS: ¿qué se completó en este trimestre según los informes?

3. PROBLEMAS RECURRENTES: ¿qué problemas o riesgos aparecen
   en más de un informe?

4. PUNTOS DE ATENCIÓN: ¿qué debería revisarse para el próximo
   trimestre?

Tono: ejecutivo, directo, sin relleno.
Extensión: máximo 2 páginas.
```

---

## Caso práctico: Estructura de carpetas para proyecto nuevo

```text
Crea una estructura de carpetas para un proyecto llamado
"Migración-ERP-2025" con las siguientes necesidades:

- Documentación del proyecto (actas, informes de estado, presentaciones)
- Datos y análisis (hojas de cálculo, datos de migración, informes)
- Contratos y legal (acuerdos, NDAs, condiciones)
- Comunicaciones (emails importantes, notas de reuniones)
- Entregables (documentos finales por fase)

Dentro de cada carpeta, crea un archivo README.md breve que explique
qué debe ir ahí y las convenciones de nomenclatura.

Crea también un archivo "00-INDICE-PROYECTO.md" en la raíz con
el índice completo de la estructura y un espacio para el estado
del proyecto.
```
