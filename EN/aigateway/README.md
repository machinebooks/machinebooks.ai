# Anatomy of a Corporate AI Platform — Sample code

> **How the engine of a corporate AI platform is built, from the inside**

Code extracted from the English chapters of the book **"Anatomy of a Corporate AI Platform"** by Carlos Pérez González and Juan Carlos Montes Senra.
Part of the series **The Professional and the Machine** (book 13).

Each file contains a didactic code block exactly as it appears in the book.
Comments and variable names are in the original language of the chapter.
The case study is **N7xGateway** (FastAPI + SQLAlchemy 2, MySQL, Redis, Celery).

## Structure

Files are organized by chapter (`cap-XX/`). The block number (`block-NN`) is the
index of the code block within the chapter, so the numbering has gaps: diagrams
(Mermaid) and plain-text blocks are not extracted but still consume an index.

Each file includes a header comment pointing to its source chapter.

## Important

These are **didactic code examples from the book**, not a runnable application.

- API keys use placeholders (`<YOUR_API_KEY>`, `<N7X_MASTER_KEY>`)
- Each file illustrates a pattern and may need dependencies, helpers, and chapter context
- Python 3.11+ with type hints; TypeScript for the admin panel / user portal

## The book

Available on Amazon:
- **English**: *Anatomy of a Corporate AI Platform* — Carlos Pérez González and Juan Carlos Montes Senra
- **Spanish**: *Anatomía de una Plataforma IA Corporativa*

Part of the series **The Professional and the Machine**.
More at [machinebooks.ai](https://machinebooks.ai/).

## License

MIT — See [LICENSE](../../LICENSE) for details.

## Scope of the published material

A file being present does not establish execution, complete coverage, or synchronization with the edition you are reading. ES contains extracted code; EN may contain a different selection or exercises. Named providers and clients identify concrete cases; alternatives need separate capability, permission, privacy, quality, and cost checks.

See [LICENSE](../../LICENSE) and [LICENSING.md](../../LICENSING.md) for the boundaries of companion code, editorial text, and production tooling.
