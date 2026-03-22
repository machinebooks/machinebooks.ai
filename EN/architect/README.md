# The Architect and the Machine — Code Examples

> **Decisions, Code, and Lessons from an Enterprise AI Project**

Code examples from the book **"The Architect and the Machine"** (*El Arquitecto y la Máquina*) by Carlos Perez Gonzalez and Juan Carlos Montes Senra. Part of the series **The Professional and the Machine**.

Each file corresponds to one or more chapters and contains the didactic code patterns explained in the book. This is the most comprehensive companion code in the series, covering the full stack of an enterprise AI platform: backend, AI service, agents, guardrails, and infrastructure.

## Available on Amazon

- **Spanish**: [*El Arquitecto y la Máquina*](https://www.amazon.com/dp/B0F192HJR6)
- **English**: [*The Architect and the Machine*](https://www.amazon.com/dp/B0F1B9TFN5)

## Requirements

| Tool | Version |
|------|---------|
| Python | 3.11+ |
| Docker & Docker Compose | Latest stable |
| Redis | 7+ (provided via Docker) |

You will also need:
- An [Anthropic API key](https://console.anthropic.com/) for the AI agents and Quality Scorer

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/SYLVARCON2049/machinebooks.ai.git
cd machinebooks.ai/architect

# 2. Copy and configure environment variables
cp .env.example .env
# Edit .env with your API keys

# 3. Start infrastructure (MySQL, Redis, Qdrant, Meilisearch)
docker compose up -d

# 4. Run the Quality Scorer tests (no infrastructure needed)
python tests/test_quality_scorer.py
```

## Chapter Map

| Chapter | File(s) | Pattern |
|---------|---------|---------|
| 5 | `backend/models/base_model.py` | BaseModel with audit, soft delete, multi-bind config |
| 5 | `backend/models/operations.py` | Client, Project, Proposal, Opportunity models |
| 5, 11 | `backend/models/ai.py` | LLMServiceConfig, LLMUsageLog, LLMModelPricing, LLMQualityScore |
| 6 | `backend/auth/jwt_handler.py` | JWT with Redis blocklist, MFA verification |
| 6 | `backend/auth/rbac.py` | RBAC multi-app: platform_guard + require_permission + rate_limit |
| 8 | `backend/tasks/celery_config.py` | 4 workers, 7 queues, 14 Beat tasks |
| 9 | `backend/routes/proposals.py` | Proposal state machine (7 states, 5 types) |
| 11 | `ai_service/llm_factory.py` | LLM Factory with fallback chains, audit, multi-level cache |
| 12 | `ai_service/rag_service.py` | RAG with Qdrant, 5 chunking strategies, access control |
| 14 | `ai_service/agents/base_agent.py` | AgentDefinition, SecurityContext, Universal Tools |
| 14 | `ai_service/agents/orchestrator.py` | Copilot Orchestrator (3 modes), Team DAG executor |
| 14 | `ai_service/agents/document_analyzer.py` | Specialized document analysis agent |
| 14 | `ai_service/guardrails/input_validator.py` | Prompt injection detection + PII filter |
| 11 | `ai_service/guardrails/token_tracker.py` | Budget enforcement, ROI calculation, pricing |
| 19 | `tests/test_quality_scorer.py` | Quality Scorer with 3 profiles, 7 metrics |
| 20 | `docker-compose.yml` | 17 services across 5 layers |

## Structure

```
architect/
├── README.md
├── .env.example                          # All required environment variables
├── docker-compose.yml                    # 17 services (simplified from 400+ line production file)
├── backend/
│   ├── models/
│   │   ├── base_model.py                # BaseModel + multi-bind configuration
│   │   ├── operations.py                # Business domain: Client, Project, Proposal
│   │   └── ai.py                        # AI governance: config, usage, pricing, quality
│   ├── auth/
│   │   ├── jwt_handler.py               # JWT lifecycle + Redis blocklist + MFA
│   │   └── rbac.py                      # 3-layer authorization pipeline
│   ├── routes/
│   │   └── proposals.py                 # Proposal state machine + AI generation
│   └── tasks/
│       └── celery_config.py             # Worker topology + Beat schedule
├── ai_service/
│   ├── llm_factory.py                   # Multi-provider LLM Factory
│   ├── rag_service.py                   # RAG with Qdrant + document loading
│   ├── agents/
│   │   ├── base_agent.py                # Agent types, SecurityContext, Universal Tools
│   │   ├── orchestrator.py              # 3-mode Orchestrator + Team DAG executor
│   │   └── document_analyzer.py         # Specialized analysis agent
│   └── guardrails/
│       ├── input_validator.py           # Prompt injection + PII detection
│       └── token_tracker.py             # Budget enforcement + ROI calculation
└── tests/
    └── test_quality_scorer.py           # Quality Scorer: 3 profiles, 7 metrics, 5 tests
```

## Stack

| Layer | Technology |
|-------|-----------|
| Development | Claude Code (claude-sonnet-4-6 / claude-opus-4-6) |
| Backend | Flask 3.0 + SQLAlchemy 2.0 (22 blueprints, 190+ endpoints) |
| AI Service | FastAPI + LangChain + Claude Agent SDK |
| Frontend | React 18 + Vite + TypeScript + Tailwind (3 apps) |
| Vectors | Qdrant v1.7 (13 collections, ~3.9M vectors) |
| Search | Meilisearch v1.6 (~4.8M docs, <10ms) |
| Database | MySQL 8.0 (3 schemas, 90+ models) |
| Queues | Celery 5.3 + Redis 7 (4 workers, 7 queues, 14 Beat tasks) |
| Containers | Docker Compose (17 services) |

## Important

These are **code examples from the book**, not a runnable application. They illustrate architectural patterns and decisions explained in each chapter.

- API keys use placeholders (`<YOUR_API_KEY>` or `os.getenv()`)
- Each file is self-contained with chapter references in comments and docstrings
- Python 3.11+ with type hints throughout
- Models use Claude exclusively: `claude-opus-4-6`, `claude-sonnet-4-6`, `claude-haiku-4-5`

## License

MIT License. See [LICENSE](../LICENSE) for details.

## The Book

*The Architect and the Machine* covers the complete architecture of an enterprise AI platform — from database design and IAM to LLM integration, agent orchestration, and Docker deployment. These code examples get you started. The book shows you where to go.
