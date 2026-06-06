# Anatomía de una Plataforma IA Corporativa — Código de ejemplo

> **Cómo se construye, por dentro, el motor de una plataforma de IA corporativa**

Código extraído de los capítulos en español del libro **"Anatomía de una Plataforma IA Corporativa"** de Carlos Pérez González y Juan Carlos Montes Senra.
Parte de la serie **El Profesional y la Máquina** (libro 13).

Cada fichero contiene bloques de código didáctico tal y como aparecen en el libro.
Los comentarios y nombres de variables están en el idioma original del capítulo.
El caso de estudio es **N7xGateway** (FastAPI + SQLAlchemy 2, MySQL, Redis, Celery).

## Estructura

Los ficheros se organizan por capítulo (`cap-XX/`). El número de bloque
(`block-NN`) es el índice del bloque de código dentro del capítulo, por lo que
la numeración tiene huecos: los diagramas (Mermaid) y los bloques de texto no
se extraen pero sí consumen índice.

Cada fichero incluye un comentario de cabecera indicando el capítulo de origen.

## Importante

Estos son **ejemplos de código del libro**, no una aplicación ejecutable.

- Las claves API usan marcadores (`<TU_API_KEY>`, `<N7X_MASTER_KEY>`)
- Cada fichero es autocontenido y comentado
- Python 3.11+ con type hints; TypeScript para el panel/portal

## El libro

Disponible en Amazon:
- **Español**: *Anatomía de una Plataforma IA Corporativa* — Carlos Pérez González y Juan Carlos Montes Senra
- **Inglés**: *Anatomy of a Corporate AI Platform*

Parte de la serie **El Profesional y la Máquina**.
Más información en [machinebooks.ai](https://machinebooks.ai/).

## Licencia

MIT — Ver [LICENSE](../../LICENSE) para más detalles.
