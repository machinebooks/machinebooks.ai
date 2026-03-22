# Source: The FinOps Engineer and the Machine -- Chapter 3
# Pattern: Claude agent for TCO analysis and recommendations

# cost_analyst_agent.py
# Agent that analyzes the TCO report and generates recommendations.
# Uses claude-sonnet-4-6: deep reasoning without the cost of claude-opus-4-6.

import anthropic

ANALYSIS_PROMPT = """You are a FinOps analyst specializing in AI-powered platforms.
You receive a TCO report in JSON and must produce:
1. A 3-paragraph executive summary (for the CFO, no technical jargon).
2. The three most important inefficiencies ranked by economic impact.
3. The two optimization actions with the highest ROI for next quarter.

Be direct. Use concrete numbers. If a service costs more than 20% of the total
infrastructure without clear justification, flag it explicitly."""

def analyze_tco_with_claude(report_json: str) -> str:
    """Sends the TCO report to Claude for analysis and recommendations."""
    client = anthropic.Anthropic()

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=ANALYSIS_PROMPT,
        messages=[{
            "role": "user",
            "content": f"Analyze this TCO report:\n\n
