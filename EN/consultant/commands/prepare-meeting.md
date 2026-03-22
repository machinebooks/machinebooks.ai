<!-- Source: The Consultant and the Machine -- Chapter 3 -->
<!-- Pattern: Custom command: meeting preparation -->

# .claude/commands/prepare-meeting.md
# Purpose: prepare a structured briefing before a client meeting

Prepare a briefing for the client meeting.

## Expected inputs
The user will provide:
- Client name or reference
- Meeting objective
- Known attendees and their roles
- Additional relevant context

## Instructions

1. **Search for historical context.** Query the knowledge base to
   find previous projects with this client, prior deliverables,
   documented decisions, and lessons learned.

2. **Regulatory analysis.** Identify the regulatory frameworks applicable
   to the client's sector (ENS, ISO 27001, DORA, AI Act, NIS2, GDPR)
   and summarize relevant changes since last contact.

3. **Prepare suggested agenda.** Propose a 60-minute agenda with:
   - 5 min: context and objective
   - 20 min: analysis/findings presentation
   - 20 min: discussion and questions
   - 10 min: next steps and commitments
   - 5 min: closing

4. **Generate briefing.** 2-3 page document with:
   - Client context (sector, size, regulation)
   - History with our practice
   - Known friction points
   - Client objectives for this meeting
   - Our position and recommendation
   - Questions we should ask
   - Questions we may be asked and prepared answers

5. **Flag risks.** List of sensitive topics to avoid or handle
   carefully in the meeting.

## Output format
Structured Markdown document, ready to review in 10 minutes.
