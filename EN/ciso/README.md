# The CISO and the Machine — Code Examples

Code examples from the book **"The CISO and the Machine"** (*El CISO y la Máquina*).

Each file corresponds to a chapter and contains the didactic code shown in the book.

## Chapter → File

| Chapter | File | Pattern |
|---------|------|---------|
| 3 | `backend/models/base.py` | BaseModel with multi-tenancy, audit, soft delete |
| 4, 6 | `backend/models/privacy.py` | GDPR Art. 30 treatments, Art. 33 breaches |
| 7 | `backend/models/risk.py` | Risk scenarios, assets, controls (MAGERIT/FAIR) |
| 8 | `backend/models/compliance.py` | Frameworks, controls, evidence, cross-mapping |
| 10, 11 | `backend/models/ai.py` | AI providers, service config, RAG collections |
| 10 | `backend/services/llm_factory.py` | Multi-provider LLM factory with fallback |
| 11 | `backend/services/rag_pipeline.py` | RAG indexer + semantic search over legal corpus |
| 6 | `backend/services/pii_detector.py` | PII detection (DNI, IBAN, credit cards) |
| 12 | `backend/agents/base.py` | BaseAgent with 3-phase lifecycle + tracing |
| 12 | `backend/agents/privacy_agent.py` | Privacy agent for GDPR analysis |
| 13 | `backend/agents/orchestrator.py` | Copilot orchestrator (3 modes) |
| 17 | `backend/middleware/security_headers.py` | CSP, HSTS, X-Frame-Options |
| 17 | `backend/middleware/audit.py` | Audit trail + CEF/Syslog |
| 16 | `backend/middleware/tenant.py` | Multi-tenant isolation |
| 17 | `backend/middleware/rate_limit.py` | Differentiated rate limiting |
| 13 | `backend/guardrails/prompt_injection.py` | Prompt injection detection |
| 13 | `backend/guardrails/pii_filter.py` | Input guardrails pipeline |

## Important

These are **code examples from the book**, not a runnable application. They illustrate patterns and architectural decisions explained in each chapter.

- API keys use placeholders (`<YOUR_API_KEY>`)
- Each file is self-contained and commented
- Python 3.11+ with type hints

## The Book

Available on Amazon:
- **Spanish**: *El CISO y la Máquina* — Carlos Pérez González, Juan Carlos Montes Senra
- **English**: *The CISO and the Machine*

Part of the series **The Professional and the Machine**.
