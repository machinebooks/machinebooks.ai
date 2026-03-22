# The Consultant and the Machine — Code Examples

Code examples from the book **"The Consultant and the Machine"** (*El Consultor y la Maquina*).

Each file corresponds to one or more chapters and contains the didactic code shown in the book.

## Chapter → File

### Presales (Chapters 1, 2, 8, 9)

| Chapter | File | Pattern |
|---------|------|---------|
| 1 | `presales/rfp_analysis_basic.py` | Basic RFP analysis with Claude API, RAG, Agent SDK |
| 2 | `presales/project_analysis.py` | Project modeling, automation potential, lessons learned |
| 8 | `presales/rfp_pipeline.py` | Full RFP pipeline: preprocessing, extraction, go/no-go |
| 9 | `presales/proposal_generator.py` | Proposal generation with RAG, quality gates, learning |

### Agents (Chapters 5, 12)

| Chapter | File | Pattern |
|---------|------|---------|
| 5 | `agents/compliance_agent.py` | Multi-framework compliance agent with Claude Agent SDK |
| 12 | `agents/audit_agent.py` | Automated audit agent: triage, evaluation, findings, MCP |

### RAG (Chapter 4)

| Chapter | File | Pattern |
|---------|------|---------|
| 4 | `rag/knowledge_base.py` | RAG system: ingestion, chunking, search, answer generation |
| 4 | `rag/docker-compose.yml` | Qdrant deployment for consulting knowledge base |

### Deliverables (Chapters 6, 13, 14)

| Chapter | File | Pattern |
|---------|------|---------|
| 6 | `deliverables/generator.py` | Three-phase deliverable pipeline with quality gates |
| 6 | `deliverables/gap_analysis_template.yml` | YAML template for gap analysis reports |
| 13 | `deliverables/gap_analysis.py` | Multi-framework gap analysis with deduplication |
| 13 | `deliverables/framework_mappings.yml` | Framework control mappings (ISO/ENS/NIS2) |
| 14 | `deliverables/report_pipeline.py` | Full reporting: findings, export (Word/PPT/PDF), continuous |

### Estimation (Chapters 3, 10)

| Chapter | File | Pattern |
|---------|------|---------|
| 10 | `estimation/effort_estimator.py` | AI-calibrated estimation with historical data |
| 10 | `estimation/estimation_pipeline.yml` | Estimation pipeline integration config |
| 3 | `estimation/quick_estimation.py` | Quick estimation, briefing prep, engagement flow |

### Competitive Intelligence (Chapter 11)

| Chapter | File | Pattern |
|---------|------|---------|
| 11 | `competitive/intelligence_agents.py` | Award tracking, talent analysis, market pipeline |
| 11 | `competitive/market_analysis_config.yml` | Market analysis configuration |

### Assessment (Chapters 15, 16)

| Chapter | File | Pattern |
|---------|------|---------|
| 15 | `assessment/maturity_assessment.py` | AI maturity assessment with adaptive interviews |
| 16 | `assessment/roadmap_generator.py` | AI roadmap: initiatives, prioritization, resources |

### Knowledge Management (Chapters 17, 18, 19)

| Chapter | File | Pattern |
|---------|------|---------|
| 17 | `knowledge/institutional_memory.py` | Institutional memory: ingestion, extraction, alerts |
| 18 | `knowledge/onboarding_system.py` | Onboarding: mentoring agent, simulator, tracking |
| 19 | `knowledge/lessons_learned.py` | Lessons learned: extraction, patterns, activation |

### Business (Chapters 20, 21, 22)

| Chapter | File | Pattern |
|---------|------|---------|
| 20 | `business/pricing.py` | AI-assisted pricing: models, simulation, blind spots |
| 21 | `business/productization.py` | Service productization: assessment, monitoring |
| 22 | `business/unit_economics.py` | Unit economics: cost model, ROI tracker, decisions |

### Ethics (Chapters 23, 24, 25)

| Chapter | File | Pattern |
|---------|------|---------|
| 23 | `ethics/confidentiality.py` | Confidentiality: classification, sanitization, routing |
| 23 | `ethics/confidentiality_config.yml` | Confidentiality policy per project type |
| 24 | `ethics/ai_boundaries.py` | AI boundaries: validation, fasting, decision matrix |
| 24 | `ethics/transparency_protocol.yml` | Calibrated transparency (3 levels) |
| 25 | `ethics/client_trust.py` | Trust: transparency checker, AI literacy workshops |
| 25 | `ethics/trust_protocol.yml` | Trust protocol configuration |

### Case Studies (Chapters 26, 27, 28, 29)

| Chapter | File | Pattern |
|---------|------|---------|
| 26 | `cases/security_audit_case.py` | Security audit: analysis, mapping, findings |
| 26 | `cases/security_audit_prep.yml` | Daily audit preparation config |
| 27 | `cases/technology_case.py` | Tech consulting: repo analysis, evaluation, estimation |
| 27 | `cases/technology_case_config.yml` | Technology case deliverables config |
| 28 | `cases/public_sector_case.py` | Public sector AI adoption analysis and roadmap |
| 29 | `cases/future_consulting.py` | Future: team leverage, continuous advisory |
| 29 | `cases/future_consulting_config.yml` | Practice evolution metrics |

### Claude Code Configuration (Chapter 7)

| Chapter | File | Pattern |
|---------|------|---------|
| 7 | `commands/example_claude_md.md` | Example CLAUDE.md for a consulting practice |
| 7 | `commands/example_project_claude_md.md` | Project-level CLAUDE.md for an audit |
| 7 | `commands/analyze-rfp.md` | Custom command: RFP analysis |
| 7 | `commands/generate-proposal.md` | Custom command: proposal generation |
| 7 | `commands/compliance-check.md` | Custom command: compliance verification |
| 7 | `commands/example_rules_quality.md` | Rules: deliverable quality standards |
| 7 | `commands/example_rules_anonymization.md` | Rules: anonymization requirements |
| 7 | `commands/mcp_config.json` | MCP server configuration |
| 7 | `commands/mcp_server_tools.py` | MCP server: document repository tools |
| 7 | `commands/agent_teams.py` | Agent Teams for multi-perspective RFP analysis |
| 3 | `commands/prepare-meeting.md` | Custom command: meeting preparation |
| 3 | `commands/quick-analysis.md` | Custom command: quick document analysis |

## Important

These are **code examples from the book**, not a runnable application. They illustrate patterns and architectural decisions explained in each chapter.

- API keys use placeholders (`<TU_API_KEY>`, `<TU_ANTHROPIC_KEY>`)
- Each file is self-contained and commented
- Python 3.11+ with type hints
- Code is in Spanish (matching the book) with English comments in headers

## The Book

Available on Amazon:
- **Spanish**: *El Consultor y la Maquina* — Carlos Perez Gonzalez
- **English**: *The Consultant and the Machine*

Part of the series **The Professional and the Machine**.
