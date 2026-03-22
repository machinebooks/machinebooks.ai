<!-- Source: The Consultant and the Machine -- Chapter 7 -->
<!-- Pattern: Custom command: proposal generation -->

# .claude/commands/generate-proposal.md

Generate draft technical proposal for: $ARGUMENTS

## Context sources
- Query corporate RAG for similar previous proposals
- Use the RFP requirements matrix (if it exists in the project)
- Apply the standard structure defined in CLAUDE.md

## Proposal structure
1. Understanding of client context and needs
2. Methodological approach (adapted to project type)
3. Work team (profiles, dedication, certifications)
4. Work plan (phases, milestones, deliverables per phase)
5. Effort estimation (based on similar projects)
6. Competitive differentiator (what sets us apart, with data)
7. Risk management (identification and mitigation)
8. Limitations and assumptions

## Constraints
- Style: technical and direct, without empty commercial language
- Financial data: use ranges, never exact absolute values
- Length per section: adaptable but proportionate to criterion weight
- If information is missing for a section, mark as [PENDING: information X]
