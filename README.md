# machinebooks.ai

**Companion code and exercises for "The Professional and the Machine" book series.**
**Código compañero y ejercicios de la serie "El Profesional y la Máquina".**

Each book documents how a specific professional profile builds enterprise systems or transforms their work using AI as the primary tool. Code is organized by language:

- **[`EN/`](EN/)** — English: curated code examples with full READMEs and chapter maps
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

All books are available on Amazon in Spanish and English. Visit **[machinebooks.ai](https://machinebooks.ai/)** for details, sample chapters, and purchase links.

## How to use

```bash
# Clone the repo
git clone https://github.com/machinebooks/machinebooks.ai.git
cd machinebooks.ai

# Pick a language and book folder
cd EN/finops    # English curated examples
cd ES/finops    # Spanish code from book chapters

# Each file is self-contained — pick the pattern you need
# See the README in each folder for details
python agents/agent_budget_manager.py
```

## Important

These are **starter scaffolds and didactic code examples**, not production-ready platforms. The books are the guides — this code is the starting point.

- Code is didactic and commented with chapter references
- API keys use placeholders (`<YOUR_API_KEY>` / `<TU_API_KEY>`)
- Security patterns are implemented but should be reviewed for your specific deployment
- All offensive security tools require proper authorization before use

## Authors

**Carlos Pérez González** — AI Solutions Architect. OSCE, OSCP, OSWE, OSEP, CREST. 20+ years offensive cybersecurity + enterprise software.

**Juan Carlos Montes Senra** — Cybersecurity Architect. GCFA, GREM. Published in PHRACK #65. Forensics, malware analysis, defensive design.

## License

MIT — See [LICENSE](LICENSE) for details.
