# The Cyber Range and the Machine — Companion Code

**Companion code for "The Cyber Range and the Machine"**
(El Cyber Range y la Máquina)

- **ES**: "El Cyber Range y la Máquina" — Available on Amazon
- **EN**: "The Cyber Range and the Machine" — Available on Amazon

This is **starter scaffold code**, not a production-ready platform. The book is the guide — this code is the starting point for readers who want to build their own Cyber Range.

All code is inside the [`code/`](code/) directory. See [`code/README.md`](code/README.md) for the full directory structure, quick start guide, and chapter map.

## Quick Start

```bash
git clone https://github.com/machinebooks/machinebooks.ai.git
cd machinebooks.ai/EN/cyberrange/code
cp .env.example .env
docker compose up -d mysql redis
# The backend/frontend services require Dockerfiles that are not included.
# Supply your own builds and dependencies before starting application services.
```

## License

MIT — See root repository for details.

## Scope of the published material

A file being present does not establish execution, complete coverage, or synchronization with the edition you are reading. ES contains extracted code; EN may contain a different selection or exercises. Named providers and clients identify concrete cases; alternatives need separate capability, permission, privacy, quality, and cost checks.

See [LICENSE](../../LICENSE) and [LICENSING.md](../../LICENSING.md) for the boundaries of companion code, editorial text, and production tooling.
