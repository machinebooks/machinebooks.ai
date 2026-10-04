# The User and the Machine — Companion Code

## Version 1.1 code

The 630 educational blocks from version 1.1 are in [v1.1/blocks](v1.1/blocks). The [manifest](v1.1/manifest.json) records each chapter or section, block position, and SHA-256. Each TXT preserves the exact text, line breaks, and tabs in the final English Word manuscript; copy it to prepare tests with the dependencies and conditions stated in the book. Extraction does not establish execution or production suitability.

Earlier folders remain as material from the previous edition and may contain a different selection. Use `v1.1` for this revision. The desktop application and production core are private; there is no Community edition and none is planned. This repository publishes companion examples only.


**AI Agents for Your Daily Work: From Asking to Delegating**

The earlier `PARTE-*` folders contain a selection of Spanish prompts and exercises, organized by chapter. The `v1.1` folder contains the exact blocks from the revised English manuscript. The prompts illustrate tasks for an AI client with the required tools, permissions, and data access. Claude Code, Claude Desktop, and claude.ai are the historical examples; adapt and validate the prompt for the client you use.

## How to use

1. Find the chapter you're reading
2. Open the corresponding exercise file
3. Use the prompt in an AI client whose capabilities and permissions fit the exercise
4. Adapt paths, names, and data to your situation

## Earlier material structure

```
user/
├── PARTE-I/    — The Foundation (Chapters 1-3)
│   ├── cap-01-ejercicios.md  — Ya usas IA, pero no un agente
│   ├── cap-02-ejercicios.md  — Tu primer agente
│   └── cap-03-ejercicios.md  — Anatomía de un agente
├── PARTE-II/   — Data & Documents (Chapters 4-7)
│   ├── cap-04-ejercicios.md  — Archivos bajo control
│   ├── cap-05-ejercicios.md  — Del PDF al dato
│   ├── cap-06-ejercicios.md  — Informes que se escriben solos
│   └── cap-07-ejercicios.md  — Presentaciones con estructura
├── PARTE-III/  — Connectivity (Chapters 8-10)
│   ├── cap-08-ejercicios.md  — MCP: el puente
│   ├── cap-09-ejercicios.md  — Conectar todo
│   └── cap-10-ejercicios.md  — Construir tu conector MCP
├── PARTE-IV/   — Communication & Coordination (Chapters 11-14)
│   ├── cap-11-ejercicios.md  — Email inteligente
│   ├── cap-12-ejercicios.md  — Calendario y tareas
│   ├── cap-13-ejercicios.md  — Reuniones
│   └── cap-14-ejercicios.md  — Gestión de proyectos
├── PARTE-V/    — Data & Visualization (Chapters 15-18)
│   ├── cap-15-ejercicios.md  — Excel y CSV
│   ├── cap-16-ejercicios.md  — Datos financieros
│   ├── cap-17-ejercicios.md  — Bases de datos sin miedo
│   └── cap-18-ejercicios.md  — Visualización instantánea
├── PARTE-VI/   — Operations (Chapters 19-22)
│   ├── cap-19-ejercicios.md  — Tu terminal potenciada
│   ├── cap-20-ejercicios.md  — Servidores y servicios
│   ├── cap-21-ejercicios.md  — La nube desde el CLI
│   └── cap-22-ejercicios.md  — Contenedores y despliegues
├── PARTE-VII/  — Automation & Workflows (Chapters 23-25)
│   ├── cap-23-ejercicios.md  — Tareas recurrentes
│   ├── cap-24-ejercicios.md  — Pipelines de datos
│   └── cap-25-ejercicios.md  — Agentes en equipo
├── PARTE-VIII/ — Governance & Caution (Chapters 26-27)
│   ├── cap-26-ejercicios.md  — Qué NO delegar
│   └── cap-27-ejercicios.md  — Privacidad y datos sensibles
└── PARTE-IX/   — Synthesis (Chapter 28)
    └── cap-28-ejercicios.md  — Tu segundo cerebro operativo
```

## Book

- **ES**: *El Usuario y la Máquina* — Available on Amazon
- **EN**: *The User and the Machine* — Available on Amazon

## Notes

- Prompts in the earlier `PARTE-*` folders are in Spanish. The `v1.1` blocks follow the revised English manuscript, including any retained technical identifiers or original examples.
- Paths use Windows format (`C:\Users\...`) by default — adapt to your OS.
- Replace placeholder values (`TU_USUARIO`, `tu-token`, file paths) with your actual data.
- No real API keys, credentials, or personal data are included in any exercise.

## Scope of the published material

A file being present does not establish execution, complete coverage, or synchronization with the edition you are reading. ES contains extracted code; EN may contain a different selection or exercises. Named providers and clients identify concrete cases; alternatives need separate capability, permission, privacy, quality, and cost checks.

See [LICENSE](../../LICENSE) and [LICENSING.md](../../LICENSING.md) for the boundaries of companion code, editorial text, and production tooling.
