# The FinOps Engineer and the Machine -- Code Examples

Code examples from the book **"The FinOps Engineer and the Machine"** (*El FinOps Engineer y la Máquina*).

Each file corresponds to a chapter and contains the didactic code shown in the book.

## Structure

| Folder | Contents | Chapters |
|--------|----------|----------|
| `tracking/` | LLMUsageLog, cost tracking, usage recording, pricing | 1-4, 6 |
| `budgets/` | BudgetConfig, budget alerts, circuit breakers, enforcement | 6, 11 |
| `roi/` | ROITracker, unit economics, TCO, business case, value calculation | 1, 17-19, 23 |
| `agents/` | Cloud cost agents, anomaly detection, rightsizing, waste, forecasting | 3, 5, 12-16, 20, 22, 28-29 |
| `dashboards/` | Cost dashboards, React components (TSX), budget status | 7, 17, 19, 23-24, 28-29 |
| `optimization/` | Model routing, caching, batch, multi-provider, embedding | 8-10, 22 |
| `cloud_apis/` | AWS Cost Explorer, Azure Cost Management, GCP Billing | 1, 5-6, Appendix B |
| `infrastructure/` | Docker configs, Grafana, Celery Beat | 3, 5, 7, 9, 12 |
| `governance/` | Policy as code, AI Act audit, GDPR, tagging policies | 5, 20-21 |
| `culture/` | FinOps culture, gamification, cost awareness | 24 |
| `cases/` | Case studies: token optimization, cloud costs, SaaS pricing | 25-27 |

## Chapter -> File

| Chapter | File | Pattern |
|---------|------|---------|
| 1 | `tracking/llm_usage_log.py` | LLMUsageLog model -- atomic record per LLM call |
| 1 | `tracking/llm_model_pricing.py` | LLMModelPricing -- price catalog per model |
| 1 | `tracking/finops_summary_router.py` | Unified FinOps summary endpoint (3 pillars) |
| 1 | `cloud_apis/cloud_cost_fetcher.py` | AWS Cost Explorer daily cost fetcher |
| 1 | `roi/task_completion_log.py` | TaskCompletionLog -- AI task vs human baseline |
| 2 | `tracking/llm_pricing_model.py` | LLMModelPricing with cache pricing fields |
| 2 | `tracking/cost_calculator.py` | Cost calculator with prompt caching support |
| 2 | `tracking/seed_llm_pricing.py` | Seed data for LLM pricing table |
| 2 | `tracking/pricing_service.py` | PricingService with fallback and unknown model logging |
| 3 | `tracking/cost_report_generator.py` | TCO report data structures and generation |
| 3 | `tracking/user_cost_profile.py` | User cost profiling (power/average/light) |
| 3 | `agents/cost_analyst_agent.py` | Claude agent for TCO analysis and recommendations |
| 3 | `infrastructure/manual_costs.yaml` | Manual cost imputations config |
| 3 | `infrastructure/cloud_costs.yaml` | Cloud cost configuration by service |
| 4 | `tracking/astream_with_tracking.py` | Streaming LLM call with cost tracking |
| 4 | `tracking/langchain_cost_callback.py` | LangChain callback handler for cost tracking |
| 4 | `tracking/llm_usage_log_full.py` | Full LLMUsageLog model (28 fields) |
| 4 | `tracking/llm_usage_tracker.py` | LLMUsageTracker -- decorator pattern for cost tracking |
| 4 | `tracking/native_usage_tracker.py` | Native Anthropic SDK usage tracker |
| 4 | `tracking/llm_pricing_service.py` | LLM pricing lookup service |
| 4 | `tracking/llm_usage_router.py` | FastAPI router for LLM usage queries |
| 4 | `tracking/tracking_validation.py` | Monthly tracking completeness validation |
| 5 | `agents/tag_audit_agent.py` | Claude agent for tag compliance audit |
| 5 | `cloud_apis/tagging_compliance_router.py` | Tagging compliance API endpoint |
| 5 | `cloud_apis/tagging_audit_task.py` | Celery task for periodic tag audit |
| 5 | `cloud_apis/apply_tag_corrections.py` | Apply approved tag corrections to AWS resources |
| 5 | `governance/tagging-policy.yaml` | Tagging policy configuration |
| 5 | `governance/validate_terraform_tags.py` | Terraform tag validation script |
| 5 | `infrastructure/docker-compose-tagged.yaml` | Docker Compose with FinOps labels |
| 6 | `budgets/budget_counter.py` | BudgetCounter model for real-time spend tracking |
| 6 | `budgets/budget_config.py` | BudgetConfig model with multi-level scopes |
| 6 | `budgets/budget_check.py` | Budget checking service with Redis caching |
| 6 | `budgets/budget_status_endpoint.py` | Budget status dashboard endpoint |
| 6 | `tracking/attribution_router.py` | Attribution and showback API endpoints |
| 6 | `tracking/unified_attribution.py` | Unified attribution: LLM + cloud costs |
| 6 | `cloud_apis/aws_cost_categories.py` | AWS Cost Categories for cost attribution |
| 7 | `dashboards/dashboard_engineering.py` | Engineering-level dashboard endpoint |
| 7 | `dashboards/dashboard_cfo.py` | CFO-level dashboard endpoint |
| 7 | `dashboards/AIMetricsTab.tsx` | React KPI card component for AI metrics |
| 7 | `dashboards/budget_status_router.py` | Budget status with burndown rate |
| 7 | `dashboards/monthly_report.py` | AI-generated monthly cost report |
| 7 | `infrastructure/grafana-budget-alert.yaml` | Grafana alert rules for budget monitoring |
| 8 | `optimization/llm_config.py` | LLM service configuration model |
| 8 | `optimization/model_router.py` | Model router -- route tasks to cheapest capable model |
| 8 | `optimization/llm_service_routing.py` | LLM service with routing integration |
| 8 | `optimization/routing_audit.py` | Routing audit task -- validate quality per model |
| 8 | `optimization/routing_quality_monitor.py` | Quality monitoring for routed requests |
| 8 | `optimization/routing_quality_sampling.py` | Statistical sampling for routing quality |
| 9 | `optimization/semantic_cache.py` | Semantic cache for LLM responses |
| 9 | `optimization/caching_middleware.py` | Anthropic caching middleware with cost tracking |
| 9 | `optimization/llm_usage_log_cache.py` | LLMUsageLog extension with cache fields |
| 9 | `optimization/batch_processing.py` | Batch processing with Anthropic Message Batches API |
| 9 | `optimization/context_manager.py` | Context window manager for token optimization |
| 9 | `optimization/document_extraction.py` | Document field extraction with prompt caching |
| 9 | `infrastructure/celery_beat_schedule.yaml` | Celery Beat schedule for periodic tasks |
| 10 | `optimization/llm_factory.py` | Multi-provider LLM factory with cost tracking |
| 10 | `optimization/tco_analysis.py` | TCO calculator: self-hosted vs API deployment |
| 10 | `optimization/embedding_service.py` | Embedding service with local/API routing |
| 11 | `budgets/budget_config_full.py` | BudgetConfig model (full version) |
| 11 | `budgets/budget_enforcement.py` | Budget enforcement middleware |
| 11 | `budgets/financial_circuit_breaker.py` | Financial circuit breaker (open/half-open/closed) |
| 11 | `budgets/llm_service_with_budgets.py` | LLM service with budget + circuit breaker |
| 11 | `budgets/budget_renewal.py` | Budget renewal Celery task |
| 11 | `budgets/budget_dashboard_api.py` | Budget dashboard API |
| 11 | `budgets/graceful_degradation.py` | Graceful degradation when budget exceeded |
| 12 | `agents/cloud_billing_mcp_server.py` | MCP server for cloud billing tools |
| 12 | `agents/cloud_cost_agent.py` | Cloud cost agent using MCP + Claude |
| 12 | `agents/cloud_agent_router.py` | FastAPI router for cloud agent queries |
| 12 | `infrastructure/docker-compose-cloud-agent.yaml` | Docker Compose for cloud agent + MCP |
| 13 | `agents/cloud_cost_metric.py` | CloudCostMetric model for time-series data |
| 13 | `agents/anomaly_detection.py` | Statistical anomaly detection (Z-score, IQR) |
| 13 | `agents/anomaly_llm_analyzer.py` | Claude-powered anomaly root cause analysis |
| 13 | `agents/business_context.py` | Business context provider for anomaly analysis |
| 14 | `agents/rightsizing_tools.py` | Rightsizing agent tools (EC2, RDS metrics) |
| 14 | `agents/rightsizing_agent.py` | Claude agent for rightsizing recommendations |
| 14 | `agents/rightsizing_router.py` | FastAPI routes for rightsizing |
| 14 | `agents/rightsizing_executor.py` | Safe execution of rightsizing actions |
| 15 | `agents/waste_scanner.py` | Automated waste scanner (EBS, EIP, snapshots) |
| 15 | `agents/waste_risk_classifier.py` | Risk classifier for waste cleanup actions |
| 15 | `agents/waste_cleanup.py` | Waste cleanup task with safety guards |
| 15 | `agents/waste_router.py` | FastAPI routes for waste management |
| 15 | `agents/orphan_snapshot_scanner.py` | Orphan snapshot detection |
| 16 | `agents/cost_forecast_model.py` | CostForecast model |
| 16 | `agents/statistical_engine.py` | Statistical forecasting (triple exponential smoothing) |
| 16 | `agents/llm_adjuster.py` | LLM-powered forecast adjustment with business context |
| 16 | `agents/forecasting_task.py` | Celery forecasting pipeline |
| 16 | `agents/token_forecaster.py` | Token-specific cost forecasting |
| 16 | `agents/forecasting_router.py` | FastAPI routes for forecasting |
| 16 | `agents/forecast_evaluation.py` | Forecast accuracy evaluation |
| 17 | `roi/roi_models.py` | HumanBaseline and ROIRecord models |
| 17 | `roi/roi_tracker.py` | ROITracker -- main calculation and period summary |
| 17 | `roi/roi_router.py` | FastAPI endpoints for ROI data |
| 17 | `roi/seed_baseline.py` | Initial HumanBaseline seed data |
| 17 | `roi/roi_integration.py` | ROITracker integration in generation flow |
| 17 | `roi/baseline_review.py` | Quarterly baseline review automation |
| 17 | `roi/roi_with_engineering.py` | ROI calculation including engineering investment |
| 17 | `roi/roi_analyzer_agent.py` | Agent for diagnosing ROI drops |
| 17 | `dashboards/ROIDashboard.tsx` | Executive ROI dashboard React component |
| 18 | `roi/business_case_generator.py` | Business case generator for CFO presentations |
| 18 | `roi/business_case_router.py` | FastAPI routes for business case generation |
| 18 | `roi/tco_table_generator.py` | TCO table generator for finance team |
| 18 | `roi/sensitivity_analysis.py` | Automated sensitivity analysis |
| 18 | `roi/narrative_generator.py` | AI-generated narrative for business case |
| 18 | `roi/npv_calculator.py` | NPV calculation for business case |
| 18 | `roi/portfolio_roi.py` | Portfolio-level ROI tracker |
| 19 | `roi/unit_economics.py` | Unit economics calculator (cost per user, per task) |
| 19 | `roi/unit_economics_router.py` | API endpoints for unit economics |
| 19 | `roi/cohort_analysis.py` | Cohort analysis for cost evolution |
| 19 | `roi/ltv_calculator.py` | LTV with non-uniform churn (survival model) |
| 19 | `roi/engagement_monitor.py` | Usage engagement monitoring |
| 19 | `roi/billing_calculator.py` | Hybrid billing model calculator |
| 19 | `roi/unit_economics_monitor.py` | Periodic unit economics monitoring task |
| 19 | `dashboards/UnitEconomicsDashboard.tsx` | Unit economics dashboard React component |
| 20 | `governance/global_policy.yaml` | Global FinOps policy definition |
| 20 | `governance/tenant_policy.yaml` | Tenant-level policy overrides |
| 20 | `governance/policy_reconciler.py` | Policy reconciler -- merge global + tenant policies |
| 20 | `governance/finops_policy_middleware.py` | FinOps policy enforcement middleware |
| 20 | `governance/validate_policies_workflow.yaml` | GitHub Actions workflow for policy validation |
| 20 | `governance/policy_audit_model.py` | Policy audit trail model |
| 20 | `governance/policy_emergency_router.py` | Emergency policy override endpoints |
| 20 | `governance/policy_metrics.py` | Policy effectiveness metrics |
| 20 | `governance/budget_alert_service.py` | Budget alert service with escalation |
| 20 | `governance/budget_policy.rego` | OPA Rego policy for budget enforcement |
| 20 | `governance/policy_correlation.py` | Policy-cost correlation analysis |
| 20 | `agents/policy_optimizer_agent.py` | AI agent for policy optimization |
| 21 | `governance/llm_audit_model.py` | LLM audit model with AI Act compliance fields |
| 21 | `governance/audit_export.py` | Audit export service (PDF, CSV, JSON) |
| 21 | `governance/audit_router.py` | Audit API endpoints |
| 21 | `governance/retention_task.py` | Data retention compliance task |
| 21 | `governance/risk_classifier.py` | AI Act risk level classifier |
| 21 | `governance/quality_scorer.py` | LLM output quality scorer |
| 21 | `governance/dts_generator.py` | Data Transparency Sheet generator |
| 21 | `governance/gdpr_content_handler.py` | GDPR content handler for LLM responses |
| 22 | `optimization/multi_llm_pricing.py` | Multi-provider pricing model |
| 22 | `optimization/provider_health.py` | Provider health monitoring |
| 22 | `optimization/failover.py` | Multi-provider failover service |
| 22 | `optimization/llm_router_multi.py` | Multi-provider LLM router |
| 22 | `optimization/providers_router.py` | Provider management API endpoints |
| 22 | `optimization/committed_use_optimizer.py` | Committed use discount optimizer |
| 22 | `optimization/model_lifecycle.py` | Model lifecycle management |
| 22 | `agents/cloud_cost_comparator.py` | Cloud cost comparator agent |
| 23 | `roi/perfil_coste.py` | Team cost profile model (PerfilCoste) |
| 23 | `roi/imputacion.py` | Cost imputation model |
| 23 | `roi/tco_calculator.py` | Full TCO calculator (people + infra + AI) |
| 23 | `roi/tco_routes.py` | TCO API routes |
| 23 | `roi/tco_analyst.py` | AI-powered TCO analysis |
| 23 | `roi/imputacion_collector.py` | Automated cost imputation collector |
| 23 | `dashboards/TCOBreakdownChart.tsx` | TCO breakdown chart React component |
| 24 | `culture/finops_culture_routes.py` | FinOps culture gamification API |
| 24 | `culture/cost_awareness_notifier.py` | Cost awareness notification service |
| 24 | `culture/finops_champion.py` | FinOps Champion program service |
| 24 | `dashboards/CostAwarenessBadge.tsx` | Cost awareness badge React component |
| 25 | `cases/document_router.py` | Document routing by operation type |
| 25 | `cases/local_preprocessor.py` | Local preprocessing before LLM call |
| 25 | `cases/cached_document_analyzer.py` | Document analyzer with semantic caching |
| 25 | `cases/context_truncator.py` | Intelligent context truncation |
| 25 | `cases/quality_evaluator.py` | Quality evaluation after optimization |
| 26 | `cases/cloud_optimizer_agent.py` | Full cloud optimization agent |
| 26 | `cases/ec2_scanner.py` | EC2 rightsizing scanner |
| 26 | `cases/optimization_pipeline.py` | Cloud optimization pipeline |
| 26 | `cases/safety_guard.py` | Safety guard for automated changes |
| 27 | `cases/pricing_calculator.py` | SaaS pricing calculator with cost model |
| 27 | `cases/pricing_benchmarker.py` | Competitive pricing benchmarker |
| 27 | `cases/fair_use_monitor.py` | Fair use monitoring for SaaS plans |
| 28 | `agents/agent_budget_manager.py` | Budget manager for autonomous agents |
| 28 | `agents/budget_aware_agent.py` | Budget-aware Claude agent |
| 28 | `agents/orchestrator_with_billing.py` | Multi-agent orchestrator with cost tracking |
| 28 | `agents/agent_session.py` | Agent session model with cost tracking |
| 28 | `dashboards/AgentCostDashboard.tsx` | Agent cost dashboard React component |
| 29 | `agents/unified_cost_event.py` | Unified cost event model (tokens + cloud + carbon) |
| 29 | `agents/carbon_token_estimator.py` | Carbon footprint estimator for LLM usage |
| 29 | `agents/convergence_analyst.py` | Convergence analyst agent |
| 29 | `agents/jevons_monitor.py` | Jevons paradox monitor |
| 29 | `dashboards/SustainabilityDashboard.tsx` | Sustainability dashboard React component |
| App. B | `cloud_apis/aws_cost_explorer.py` | AWS Cost Explorer examples |
| App. B | `cloud_apis/aws_cur.py` | AWS Cost and Usage Reports setup |
| App. B | `cloud_apis/aws_savings_plans.py` | AWS Savings Plans and RI coverage queries |
| App. B | `cloud_apis/azure_cost_management.py` | Azure Cost Management examples |
| App. B | `cloud_apis/azure_budgets.py` | Azure Budget creation |
| App. B | `cloud_apis/azure_advisor.py` | Azure Advisor cost recommendations |
| App. B | `cloud_apis/gcp_billing.py` | GCP Cloud Billing API examples |
| App. B | `cloud_apis/gcp_budgets.py` | GCP Budget alerts setup |
| App. B | `cloud_apis/gcp_bigquery_export.py` | GCP BigQuery billing export |
| App. B | `cloud_apis/multi_cloud_agent.py` | Multi-cloud cost agent with Claude |

## Important

These are **code examples from the book**, not a runnable application. They illustrate patterns and architectural decisions explained in each chapter.

- API keys use placeholders (`<YOUR_API_KEY>`)
- Each file is self-contained and commented
- Python 3.11+ with type hints
- TypeScript/TSX for React dashboard components

## The Book

Available on Amazon:
- **Spanish**: *El FinOps Engineer y la Máquina* -- Carlos Pérez González
- **English**: *The FinOps Engineer and the Machine*

Part of the series **The Professional and the Machine**.
