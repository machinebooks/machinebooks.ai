<!-- Source: The Consultant and the Machine -- Chapter 7 -->
<!-- Pattern: Custom command: compliance verification -->

# .claude/commands/compliance-check.md

Run compliance verification against: $ARGUMENTS

## Process
1. Identify the reference framework (ISO 27001, ENS, NIS2, DORA, AI Act)
2. Load applicable controls/measures from the regulatory RAG
3. Cross-reference against available evidence in the project directory
4. Generate compliance matrix: control -> status -> evidence -> gap

## Valid statuses
- COMPLIANT: sufficient documented evidence
- PARTIALLY COMPLIANT: incomplete evidence or partial implementation
- NON-COMPLIANT: no evidence or evidence of non-compliance
- NOT APPLICABLE: documented exclusion justification
- NOT EVALUATED: insufficient information available

## Output format
Markdown table with columns:
| Control ID | Description | Status | Evidence | Gap | Priority |

Followed by:
- Statistical summary (% by status)
- Top 10 gaps by criticality
- Prioritized recommendations (Quick win / Medium term / Long term)
