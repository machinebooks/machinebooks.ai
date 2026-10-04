# PQC-Day and the Machine — Companion Code

## Code from version 1.1

The 224 educational blocks from version 1.1 are in [v1.1/blocks](v1.1/blocks). The [manifest](v1.1/manifest.json) records each section, position and SHA-256, together with the final Word and EPUB hashes. Each TXT preserves the text, line breaks and tabs of its corresponding Word file; it can be copied to prepare tests with the conditions and dependencies described in the book. Extraction does not establish execution or production suitability.

Earlier folders belong to the previous edition material and may contain another selection. The reference for this revision is `v1.1`. The product and its core are private; no Community edition exists or will be published. This folder publishes companion examples only.

**Decisions, Code, and Lessons from a Post-Quantum Readiness Platform Built with AI**

This repository contains the didactic code examples from the book. Each file illustrates a pattern discussed in the corresponding chapter. Dependencies, configuration and integration must be prepared and checked before execution.

> **Important**: These are didactic examples, not production code. They are simplified and anonymized versions of real patterns. Do not use them directly in production without proper security review, error handling, and testing.

## Book

- **ES**: "PQC-Day y la Máquina" — Available on Amazon
- **EN**: "PQC-Day and the Machine" — Available on Amazon

## Requirements of the earlier material

- **Python 3.11+** — Backend examples
- **Node.js 18+** — Frontend examples (cap-19)
- **Docker & Docker Compose** — Infrastructure examples (cap-21)
- **Optional**: `pip install anthropic` for AI-powered examples (cap-11, 12, 13, 26)

## Earlier material: preparation examples

```bash
# Clone the repository
git clone https://github.com/machinebooks/machinebooks.ai.git
cd machinebooks.ai/EN/pqc-day

# Copy environment variables
cp .env.example .env
# Edit .env with your values

# Run any example
python cap-01/crypto_scanner_basic.py /path/to/your/code
python cap-07/repository_analyzer.py /path/to/your/code
python cap-18/priority_scoring.py
```

## Structure of the earlier material

```
pqc-day/
├── README.md                              # This file
├── .env.example                           # Environment variables template
├── docker-compose.yml                     # Minimal local setup (MySQL + Redis)
│
├── cap-01/
│   └── crypto_scanner_basic.py            # Basic quantum-vulnerable crypto scanner
│                                          # + Claude API classification
│
├── cap-07/
│   ├── crypto_patterns.py                 # CRYPTO_PATTERNS dictionary (6 languages)
│   └── repository_analyzer.py             # RepositoryAnalyzer with PQC scoring
│
├── cap-08/
│   └── certificate_scanner.py             # URLCertificateScanner: TLS + PQC support
│                                          # detection (ML-KEM, hybrid groups)
│
├── cap-09/
│   ├── quantum_vulnerable_algorithms.py   # Algorithm classification dictionary
│   └── cloud_security_analyzer.py         # CloudSecurityAnalyzer: AWS KMS, S3
│
├── cap-10/
│   └── owasp_analyzer.py                  # OWASPAnalyzer: Top 10 pattern detection
│
├── cap-11/
│   └── ai_code_analyzer.py               # Multi-provider AI code analysis
│                                          # (Claude API, prompt engineering)
│
├── cap-12/
│   ├── agent.py                           # CodeAnalysisAgent (tool-calling loop)
│   └── tools.py                           # RepositoryTools (5 tools)
│
├── cap-13/
│   └── rag_service.py                     # RAG: chunking, search, reranking
│                                          # with PQC synonym expansion
│
├── cap-14/
│   └── ai_admin_models.py                 # AI governance: Provider, Service,
│                                          # Prompt, UsageLog, Controls (C.VR.1-12)
│
├── cap-15/
│   ├── compliance_models.py               # Framework, Control, Assessment models
│   └── compliance_service.py              # Finding-to-control mapping (NIS2/DORA)
│
├── cap-18/
│   └── priority_scoring.py               # Europol framework: shelf life, exposure,
│                                          # severity, migration complexity
│
├── cap-19/
│   └── Dashboard.jsx                      # React + MUI dashboard component
│
├── cap-21/
│   ├── docker-compose.yml                 # Full 7-service Docker Compose
│   └── nginx.conf                         # Nginx reverse proxy configuration
│
├── cap-22/
│   └── celery_tasks.py                    # Celery async tasks (repository analysis)
│
└── cap-26/
    ├── monitoring_agent.py                # Continuous monitoring agent (Claude)
    └── crypto_policy.py                   # CryptoPolicy: crypto-agility data model
```

## Guide to the earlier material

| Chapter | File(s) | What It Shows |
|---------|---------|---------------|
| 1 | `cap-01/crypto_scanner_basic.py` | Regex-based scanner + Claude API classification |
| 7 | `cap-07/crypto_patterns.py`, `cap-07/repository_analyzer.py` | Multi-language pattern dictionary, full scanner with PQC scoring |
| 8 | `cap-08/certificate_scanner.py` | TLS certificate analysis, PQC group detection (ML-KEM, X25519MLKEM768) |
| 9 | `cap-09/quantum_vulnerable_algorithms.py`, `cap-09/cloud_security_analyzer.py` | Algorithm taxonomy, AWS KMS/S3 audit |
| 10 | `cap-10/owasp_analyzer.py` | OWASP Top 10 vulnerability detection engine |
| 11 | `cap-11/ai_code_analyzer.py` | Multi-provider AI analysis (Anthropic, OpenAI), prompt engineering, JSON parsing |
| 12 | `cap-12/agent.py`, `cap-12/tools.py` | Autonomous agent with tool-calling loop, 5 repository tools |
| 13 | `cap-13/rag_service.py` | Document chunking, PQC synonym expansion, LLM reranking |
| 14 | `cap-14/ai_admin_models.py` | AI governance: providers, services, prompts, usage logs, compliance controls |
| 15 | `cap-15/compliance_models.py`, `cap-15/compliance_service.py` | NIS2/DORA compliance models, finding-to-control mapping |
| 18 | `cap-18/priority_scoring.py` | Migration priority scoring (Europol framework) |
| 19 | `cap-19/Dashboard.jsx` | React + MUI dashboard with theme and routing |
| 21 | `cap-21/docker-compose.yml`, `cap-21/nginx.conf` | 7-service Docker architecture, Nginx reverse proxy |
| 22 | `cap-22/celery_tasks.py` | Async task pipeline with progress tracking |
| 26 | `cap-26/monitoring_agent.py`, `cap-26/crypto_policy.py` | Continuous monitoring agent, crypto-agility policy model |

## Running Examples That Use Claude API

Examples in chapters 1, 11, 12, 13, and 26 can optionally call the Claude API. To use them:

```bash
export ANTHROPIC_API_KEY=your-key-here

# Chapter 1: scan + classify
python cap-01/crypto_scanner_basic.py /path/to/code --classify

# Chapter 11: AI code analysis
python cap-11/ai_code_analyzer.py

# Chapter 12: autonomous agent
python cap-12/agent.py /path/to/repo "Analyze cryptographic posture"

# Chapter 26: monitoring agent
python cap-26/monitoring_agent.py
```

## Running Without API Keys

Most examples work without any API keys:

```bash
# Scan a directory for quantum-vulnerable cryptography
python cap-01/crypto_scanner_basic.py /path/to/your/code

# Full repository analysis with PQC scoring
python cap-07/repository_analyzer.py /path/to/your/code

# Scan certificates and check PQC support
python cap-08/certificate_scanner.py https://example.com https://google.com

# OWASP vulnerability detection
python cap-10/owasp_analyzer.py

# Migration priority scoring
python cap-18/priority_scoring.py

# Crypto-agility policy evaluation
python cap-26/crypto_policy.py

# AI governance controls
python cap-14/ai_admin_models.py

# NIS2 compliance mapping
python cap-15/compliance_service.py
```

## Historical case study stack

| Layer | Technology |
|-------|-----------|
| AI Development | Claude Code (claude-sonnet-4-6 / claude-opus-4-6) |
| Frontend | React 18 + Vite + TypeScript + MUI |
| Backend | Flask 3.0 + SQLAlchemy 2.0 |
| AI Service | Named API adapters and tool loops; SDK integration requires its version-specific contract |
| LLMs | Anthropic Claude, OpenAI, Ollama |
| Database | MySQL 8.0 |
| Queues | Celery 5.3 + Redis 7 |
| Containers | Docker Compose (7 services) |

## License

The companion examples in this folder are MIT-licensed: see [LICENSE](../../LICENSE) and [LICENSING.md](../../LICENSING.md). The book text and production tooling are outside that grant. See the book for explanations and production considerations.

## Authors

Carlos Perez Gonzalez

---

*Built with [Claude Code](https://claude.ai/claude-code)*

## Scope of the published material

A file being present does not establish execution, complete coverage, or synchronization with the edition you are reading. ES contains extracted code; EN may contain a different selection or exercises. Named providers and clients identify concrete cases; alternatives need separate capability, permission, privacy, quality, and cost checks.

See [LICENSE](../../LICENSE) and [LICENSING.md](../../LICENSING.md) for the boundaries of companion code, editorial text, and production tooling.
