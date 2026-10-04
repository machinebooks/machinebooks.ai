# machinebooks.ai

**Companion code and exercises for "The Professional and the Machine" book series.**
**Ejemplos complementarios y ejercicios de la serie "El Profesional y la Máquina".**

Each book examines how a professional profile applies AI capabilities, tool contracts, permissions, evidence, and human review to systems or work. Named providers and SDKs retain their historical attribution as implementation cases. Examples are organized by language:

- **[`EN/`](EN/)** — English: curated examples/exercises and per-folder documentation; availability varies
- **[`ES/`](ES/)** — Español: código extraído de los capítulos en español de cada libro

## The Series / La Serie

| # | English | Español | EN | ES |
|---|---------|---------|----|----|
| 1 | *The Architect and the Machine* | *El Arquitecto y la Máquina* | [`EN/architect/`](EN/architect/) | [`ES/architect/`](ES/architect/) |
| 2 | *The Cyber Range and the Machine* | *El Cyber Range y la Máquina* | [`EN/cyberrange/`](EN/cyberrange/) | [`ES/cyberrange/`](ES/cyberrange/) |
| 3 | *The CISO and the Machine* | *El CISO y la Máquina* | [`EN/ciso/`](EN/ciso/) | [`ES/ciso/`](ES/ciso/) |
| 4 | *The Pentester and the Machine* | *El Pentester y la Máquina* | [`EN/pentester/`](EN/pentester/) | [`ES/pentester/`](ES/pentester/) |
| 5 | *PQC-Day and the Machine* | *PQC-Day y la Máquina* | [`EN/pqc-day/`](EN/pqc-day/) | [`ES/pqc-day/`](ES/pqc-day/) |
| 6 | *The User and the Machine* | *El Usuario y la Máquina* | [`EN/user/`](EN/user/) | [`ES/user/`](ES/user/) |
| 7 | *The FinOps Engineer and the Machine* | *El FinOps Engineer y la Máquina* | [`EN/finops/`](EN/finops/) | [`ES/finops/`](ES/finops/) |
| 8 | *The Consultant and the Machine* | *El Consultor y la Máquina* | [`EN/consultant/`](EN/consultant/) | [`ES/consultant/`](ES/consultant/) |
| 9 | *The DevSecOps and the Machine* | *El DevSecOps y la Máquina* | [`EN/devsecops/`](EN/devsecops/) | [`ES/devsecops/`](ES/devsecops/) |
| 10 | *The Bug Bounty Hunter and the Machine* (in editing) | *El Bug Bounty Hunter y la Máquina* (en edición) | [`EN/bugbounty/`](EN/bugbounty/) | [`ES/bugbounty/`](ES/bugbounty/) |
| 11 | *AI Safety Engineer and the Machine* | *AI Safety Engineer y la Máquina* | [`EN/aisafety/`](EN/aisafety/) | [`ES/aisafety/`](ES/aisafety/) |
| 12 | *Anatomy of an Agent* | *Anatomía de un Agente de IA* | Material not available | Material no disponible |
| 13 | *Anatomy of a Corporate AI Platform* | *Anatomía de una Plataforma IA Corporativa* | [`EN/aigateway/`](EN/aigateway/) | [`ES/aigateway/`](ES/aigateway/) |

Publication status varies by title and language; the editing and unavailable-material entries above are not publication or companion-availability claims. Visit **[machinebooks.ai](https://machinebooks.ai/)** for current book details, sample chapters, and purchase links.

El estado de publicación varía por título e idioma. Las entradas en edición o con material no disponible no anuncian publicación ni disponibilidad de ejemplos. Consulta **[machinebooks.ai](https://machinebooks.ai/)** para los detalles y enlaces actuales.

## Review status — 4 October 2026

Educational blocks from the v1.1 revisions of User, FinOps, AI Safety, and PQC are separated into `ES/<book>/v1.1/` and `EN/<book>/v1.1/`, with source manifests and SHA-256 hashes. Earlier material is preserved. The other titles remain under review; this code synchronization does not itself announce eBook publication or establish execution of every snippet.

Los bloques didácticos de la revisión v1.1 de Usuario, FinOps, AI Safety y PQC están separados en `ES/<libro>/v1.1/` y `EN/<libro>/v1.1/`, con manifiestos de origen y SHA-256. El material anterior se conserva. Los demás títulos siguen en revisión; esta sincronización del código no anuncia por sí misma la publicación de los eBooks ni acredita ejecución de cada fragmento.

## How to use

```bash
# Clone the repo
git clone https://github.com/machinebooks/machinebooks.ai.git
cd machinebooks.ai

# Choose ONE language and book folder; this example selects English
cd EN/finops

# Inspect the example and its dependencies before running it
# For Spanish, start from the repository root and choose ES/finops instead
# See the README in the selected folder for requirements and limitations
```

## Important

These are **starter scaffolds and didactic code examples**, not production-ready platforms. The books are the guides — this code is the starting point.

- EN curated examples and ES extracted blocks have different structures; folder or file counts do not establish content parity.
- A file being present does not establish execution, security effectiveness, or synchronization with the edition you are reading.
- Named AI clients, SDKs, and providers identify concrete examples. Alternative adapters require their own capability, permission, privacy, quality, and cost checks.
- Code is didactic and commented with chapter references
- API keys use placeholders (`<YOUR_API_KEY>` / `<TU_API_KEY>`)
- Security patterns are implemented but should be reviewed for your specific deployment
- All offensive security tools require proper authorization before use

## Private application case and public examples

The SylvarSecDesktop case remains private. This companion repository does not offer the application source, a public application download, or a current or future Community edition. The authors authorize the published didactic fragments and tests in EN/ and ES/ under their existing MIT terms; those examples are separate from the private product core.

El caso SylvarSecDesktop permanece privado. Este repositorio no ofrece el código fuente de la aplicación, su descarga pública ni una edición Community actual o futura. Los autores mantienen autorizados los fragmentos y pruebas didácticos publicados en EN/ y ES/ bajo su licencia MIT; esos ejemplos son recursos distintos del core privado.

## Authors

**Carlos Pérez González** — AI Solutions Architect. OSCE, OSCP, OSWE, OSEP, CREST. 20+ years offensive cybersecurity + enterprise software.

**Juan Carlos Montes Senra** — Cybersecurity Architect. GCFA, GREM. Published in PHRACK #65. Forensics, malware analysis, defensive design.

## License

The companion code in `EN/` and `ES/` is MIT-licensed. Editorial content,
videocourses, trademarks, and the production tooling in `formaciones/` are outside
that grant. See [LICENSE](LICENSE) and [LICENSING.md](LICENSING.md) for the complete
boundary.
