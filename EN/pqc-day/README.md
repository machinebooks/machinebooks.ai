# PQC-Day and the Machine — Companion Code

**Decisions, Code, and Lessons from a Post-Quantum Readiness Platform Built with AI**

This repository contains the didactic code examples from the book. Each file is a self-contained, runnable example that illustrates a pattern discussed in the corresponding chapter.

> **Important**: These are didactic examples, not production code. They are simplified and anonymized versions of real patterns. Do not use them directly in production without proper security review, error handling, and testing.

## Book

- **ES**: "PQC-Day y la Máquina" — Available on Amazon
- **EN**: "PQC-Day and the Machine" — Available on Amazon

## Requirements

- **Python 3.11+** — Backend examples
- **Node.js 18+** — Frontend examples (cap-19)
- **Docker & Docker Compose** — Infrastructure examples (cap-21)
- **Optional**: `pip install anthropic` for AI-powered examples (cap-11, 12, 13, 26)

## Quick Start

```bash
# Clone the repository
git clone https://github.com/machinebooks-ai/pqc-day.git
cd pqc-day

# Copy environment variables
cp .env.example .env
# Edit .env with your values

# Run any example
python cap-01/crypto_scanner_basic.py /path/to/your/code
python cap-07/repository_analyzer.py /path/to/your/code
python cap-18/priority_scoring.py
```

## Repository Structure

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

## Chapter-by-Chapter Guide

| Chapter | File(s) | What It Shows |
|---------|---------|---------------|
| 1 | `crypto_scanner_basic.py` | Regex-based scanner + Claude API classification |
| 7 | `crypto_patterns.py`, `repository_analyzer.py` | Multi-language pattern dictionary, full scanner with PQC scoring |
| 8 | `certificate_scanner.py` | TLS certificate analysis, PQC group detection (ML-KEM, X25519MLKEM768) |
| 9 | `quantum_vulnerable_algorithms.py`, `cloud_security_analyzer.py` | Algorithm taxonomy, AWS KMS/S3 audit |
| 10 | `owasp_analyzer.py` | OWASP Top 10 vulnerability detection engine |
| 11 | `ai_code_analyzer.py` | Multi-provider AI analysis (Anthropic, OpenAI), prompt engineering, JSON parsing |
| 12 | `agent.py`, `tools.py` | Autonomous agent with tool-calling loop, 5 repository tools |
| 13 | `rag_service.py` | Document chunking, PQC synonym expansion, LLM reranking |
| 14 | `ai_admin_models.py` | AI governance: providers, services, prompts, usage logs, compliance controls |
| 15 | `compliance_models.py`, `compliance_service.py` | NIS2/DORA compliance models, finding-to-control mapping |
| 18 | `priority_scoring.py` | Migration priority scoring (Europol framework) |
| 19 | `Dashboard.jsx` | React + MUI dashboard with theme and routing |
| 21 | `docker-compose.yml`, `nginx.conf` | 7-service Docker architecture, Nginx reverse proxy |
| 22 | `celery_tasks.py` | Async task pipeline with progress tracking |
| 26 | `monitoring_agent.py`, `crypto_policy.py` | Continuous monitoring agent, crypto-agility policy model |

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

## Technology Stack (Case Study)

| Layer | Technology |
|-------|-----------|
| AI Development | Claude Code (claude-sonnet-4-6 / claude-opus-4-6) |
| Frontend | React 18 + Vite + TypeScript + MUI |
| Backend | Flask 3.0 + SQLAlchemy 2.0 |
| AI Service | Claude API + Claude Agent SDK |
| LLMs | Anthropic Claude, OpenAI, Ollama |
| Database | MySQL 8.0 |
| Queues | Celery 5.3 + Redis 7 |
| Containers | Docker Compose (7 services) |

## License

These examples are provided for educational purposes as companion material to the book. See the book for full explanations and production considerations.

## Authors

Carlos Perez Gonzalez

---

*Built with [Claude Code](https://claude.ai/claude-code)*
