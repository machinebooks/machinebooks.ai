<!-- Source: The Consultant and the Machine -- Chapter 7 -->
<!-- Pattern: Custom command: RFP analysis -->

# .claude/commands/analyze-rfp.md

Analyze the RFP document provided as argument: $ARGUMENTS

## Process
1. Extract mandatory (MUST) and scored (SHOULD) requirements
2. Identify evaluation criteria with their weights
3. Detect penalties and risk clauses
4. List required professional profiles with certifications
5. Identify deadlines (bid submission, start, duration, milestones)
6. Generate preliminary compliance matrix

## Output format
Produce a Markdown report with these sections:
- Executive summary (10 lines maximum)
- Mandatory requirements (table: ID | Requirement | We comply | Evidence)
- Evaluation criteria (table: Criterion | Weight | Our position)
- Contractual risks (prioritized list)
- Required profiles (table: Profile | Certifications | Availability)
- Critical deadlines (timeline)
- Go/no-go recommendation with justification

## Constraints
- If you cannot access the document, request content to be pasted
- Mark with a warning any ambiguous requirement needing clarification
- Do not assume compliance without evidence -- mark as "TO VERIFY"
