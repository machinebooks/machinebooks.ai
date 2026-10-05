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
| 10 | *The Bug Bounty Hunter and the Machine* | *El Bug Bounty Hunter y la Máquina* | [`EN/bugbounty/`](EN/bugbounty/) | [`ES/bugbounty/`](ES/bugbounty/) |
| 11 | *AI Safety Engineer and the Machine* | *AI Safety Engineer y la Máquina* | [`EN/aisafety/`](EN/aisafety/) | [`ES/aisafety/`](ES/aisafety/) |
| 12 | *Anatomy of an AI Agent* | *Anatomía de un Agente de IA* | [`EN/agents/`](EN/agents/) | [`ES/agents/`](ES/agents/) |
| 13 | *Anatomy of a Corporate AI Platform* | *Anatomía de una Plataforma IA Corporativa* | [`EN/aigateway/`](EN/aigateway/) | [`ES/aigateway/`](ES/aigateway/) |

Publication status varies by title and language; the editing and unavailable-material entries above are not publication or companion-availability claims. Visit **[machinebooks.ai](https://machinebooks.ai/)** for current book details, sample chapters, and purchase links.

El estado de publicación varía por título e idioma. Las entradas en edición o con material no disponible no anuncian publicación ni disponibilidad de ejemplos. Consulta **[machinebooks.ai](https://machinebooks.ai/)** para los detalles y enlaces actuales.

## Review status — 5 October 2026

All thirteen v1.1 manuscript pairs are closed locally. Educational blocks from their final Spanish and English Word manuscripts are organized in ES/<book>/v1.1/ and EN/<book>/v1.1/. Every language has a literal source manifest identifying the current Word and EPUB files and SHA-256 hashes. Earlier material outside those revision folders is preserved; earlier v1.1 snapshots remain available in Git history.

Los trece pares de manuscritos v1.1 están cerrados localmente. Los bloques didácticos de los Word finales en español e inglés están organizados en ES/<libro>/v1.1/ y EN/<libro>/v1.1/. Cada idioma dispone de un manifiesto literal que identifica los Word y EPUB actuales y sus hashes SHA-256. El material anterior situado fuera de las carpetas de revisión se conserva; los snapshots v1.1 anteriores siguen disponibles en el historial Git.

All twenty-six existing Kindle v1.1 updates, covering the thirteen books in Spanish and English, have been submitted to KDP with submission confirmation on 5 October 2026. At 14:48 UTC on that date, the KDP bookshelf showed all twenty-six Kindle editions as Live, with no updates still publishing. A subsequent administrative correction to the AI-generated cover-image disclosures was submitted for all twenty-six Kindle editions without changing their manuscripts or prices. At 16:53 UTC, eight of those administrative updates had completed and eighteen were publishing. All eighteen submitted paperback v1.1 updates were Live. FinOps, Agents, Cyber Range, and Gateway require new paperback editions under KDP page-count and format rules. Preparation continues locally and in existing drafts; KDP has reached its weekly limit for creating new paperback titles. No previous paperback has been unpublished. A two-volume paperback option is being prepared for Gateway. Paperback work remains separate from the complete Kindle books. Source extraction establishes provenance of the fragments, not execution of every example or parity from file counts.

Las veintiséis actualizaciones Kindle v1.1 existentes, correspondientes a los trece libros en español e inglés, se han enviado a KDP con confirmación de envío el 5 de octubre de 2026. A las 14:48 UTC de ese día, la biblioteca KDP muestra las veintiséis ediciones Kindle en línea, sin actualizaciones todavía publicándose. Después se enviaron las correcciones administrativas de las declaraciones de imágenes de cubierta generadas por IA de las veintiséis ediciones Kindle, sin cambiar manuscritos ni precios. A las 16:53 UTC, ocho de esas actualizaciones administrativas habían terminado y dieciocho seguían publicándose. Las dieciocho actualizaciones v1.1 de tapa blanda enviadas estaban en línea. FinOps, Agentes, Cyber Range y Gateway requieren nuevas ediciones de papel por las reglas de páginas y formato de KDP. La preparación continúa localmente y en los borradores existentes; KDP ha alcanzado su límite semanal de creación de nuevos títulos de papel. No se ha retirado ninguna edición anterior. Para Gateway se está preparando una opción de papel en dos tomos. El trabajo de papel permanece separado de los libros Kindle completos. La extracción acredita la procedencia de los fragmentos, no la ejecución de todos los ejemplos ni la paridad a partir del número de ficheros.

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
