# The DevSecOps and the Machine — Code Examples

Code examples from the book **"The DevSecOps and the Machine"** (*El DevSecOps y la Máquina*).

Each file corresponds to one or more chapters and contains the didactic code shown in the book.

## Chapter → File

| Chapter | File | Pattern |
|---------|------|---------|
| 1 | `pipeline/security_pipeline.yml` | Initial GitHub Actions security pipeline with Semgrep |
| 1 | `pipeline/triage_findings.py` | SARIF-based SAST triage with Claude |
| 2 | `sast/semgrep_rules.yml` | Custom Semgrep rules (SQL injection, XSS, SSRF taint analysis) |
| 3 | `inventory/pipeline_inventory.py` | Automated asset discovery (Docker, GitHub Actions, LLM, RAG) |
| 3 | `inventory/stride_classifier.py` | STRIDE threat modeling agent with Claude |
| 3 | `inventory/surface_discovery_agent.py` | Continuous attack surface discovery with Claude Agent SDK |
| 4 | `sast/triaje_sast.py` | Tiered SAST triage: Haiku filters, Sonnet analyzes |
| 4 | `sast/pr_comments.py` | Publish triage results as inline PR comments |
| 5 | `sca/triage_sca.py` | SCA vulnerability triage with Grype + SBOM context |
| 5 | `sca/check_dependency_policy.py` | Dependency policy enforcement (licenses, vulnerabilities) |
| 5 | `sca/dependency_policy.yml` | Dependency policy as code |
| 6 | `secrets/gitleaks.toml` | Gitleaks config with Anthropic token rules |
| 6 | `secrets/claude_secret_scanner.py` | Semantic secret detection with Claude |
| 6 | `secrets/vault_credentials.py` | HashiCorp Vault ephemeral credentials |
| 7 | `containers/analyze_trivy.py` | Contextual Trivy result analysis with Claude |
| 7 | `containers/remediation_agent.py` | Dockerfile remediation agent with Claude Agent SDK |
| 7 | `containers/kyverno_policies.yml` | Kyverno admission policies (signatures, registries, non-root) |
| 8 | `pipeline/security_aggregator.py` | Multi-tool security aggregator with gate logic |
| 9 | `agents/triage_agent.py` | Full triage agent with CVE, exposure, and correlation tools |
| 9 | `policy/triage_mandatory_rules.rego` | OPA mandatory triage rules (PCI-DSS, exploits) |
| 10 | `agents/security_review.py` | AI security code review for pull requests |
| 11 | `agents/remediation_agent.py` | Automated remediation agent with PR generation |
| 11 | `policy/remediation_exclusions.rego` | OPA exclusion policies for auto-remediation |
| 12 | `dast/dast_agent.py` | Intelligent DAST with OpenAPI analysis and ZAP orchestration |
| 13 | `ai_security/prompt_injection.py` | Multi-layer prompt injection defense |
| 14 | `ai_security/model_supply_chain.py` | Model integrity verification and behavioral drift detection |
| 15 | `ai_security/agent_security.py` | Agent permission system, rate limiting, audit trail |
| 17 | `compliance/ai_act_classifier.py` | AI Act risk classification and conformity assessment |
| 18 | `runtime/falco_rules.yml` | Falco rules for containers and AI workloads |
| 18 | `runtime/falco_agent.py` | Runtime security analysis agent with auto-response |
| 19 | `observability/security_metrics.py` | Prometheus metrics exporter for security pipeline |
| 20 | `incidents/incident_agent.py` | Incident correlation, containment, and postmortem agent |
| 21 | `policy/container_security.rego` | OPA policies for Kubernetes, deployments, and AI models |
| 22 | `compliance/compliance_engine.py` | Continuous compliance evaluation and audit preparation |
| 24 | `champions/champion_toolkit.py` | Security Champions training and gamification |
| 25 | `maturity/maturity_model.py` | DevSecOps maturity model with automated assessment |

## Directory Structure

```
devsecops/
├── agents/              # AI agents for triage, review, remediation
├── ai_security/         # Prompt injection, model supply chain, agent security
├── champions/           # Security Champions program tools
├── compliance/          # AI Act, ISO 27001, ENS compliance automation
├── containers/          # Trivy analysis, Dockerfile remediation, Kyverno
├── dast/                # OWASP ZAP orchestration, API fuzzing
├── incidents/           # Incident correlation and response
├── inventory/           # Asset discovery, STRIDE threat modeling
├── maturity/            # DevSecOps maturity assessment
├── observability/       # Prometheus metrics, security dashboards
├── pipeline/            # GitHub Actions workflows, security gate
├── policy/              # OPA/Rego policies for triage, remediation, k8s
├── runtime/             # Falco rules, runtime security agents
├── sast/                # Semgrep rules, SAST triage
├── sca/                 # SCA triage, dependency policies
└── secrets/             # Gitleaks, secret scanning, Vault integration
```

## Important

These are **code examples from the book**, not a runnable application. They illustrate patterns and architectural decisions explained in each chapter.

- API keys use placeholders (`<TU_API_KEY>`)
- Each file is self-contained and commented
- Python 3.12+ with type hints
- Claude models: `claude-sonnet-4-6`, `claude-haiku-4-5`, `claude-opus-4-6`

## The Book

Available on Amazon:
- **Spanish**: *El DevSecOps y la Máquina* — Carlos Perez Gonzalez
- **English**: *The DevSecOps and the Machine*

Part of the series **The Professional and the Machine**.
