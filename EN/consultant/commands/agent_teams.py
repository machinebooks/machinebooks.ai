# Source: The Consultant and the Machine -- Chapter 7
# Pattern: Agent Teams for multi-perspective RFP analysis
# agent_teams/rfp_response.py
from claude_agent_sdk import Agent, tool, orchestrator

# Coordinator agent -- manages the global flow
coordinator = Agent(
    name="rfp-coordinator",
    model="claude-sonnet-4-6",
    system="""You coordinate the response to an RFP. Your job:
    1. Distribute tender sections to specialized agents
    2. Integrate their analyses into a coherent view
    3. Identify contradictions between requirements
    4. Produce the consolidated go/no-go recommendation"""
)

# Technical analysis agent
tech_analyst = Agent(
    name="tech-analyst",
    model="claude-sonnet-4-6",
    system="""You analyze technical requirements from RFPs:
    - Required architecture, technologies, integrations
    - Technical feasibility with our current stack
    - Technical risks and mitigations
    - Implementation effort (days per component)"""
)

# Regulatory compliance agent
compliance_analyst = Agent(
    name="compliance-analyst",
    model="claude-sonnet-4-6",
    system="""You verify compliance requirements in RFPs:
    - Required regulatory frameworks (ISO, ENS, NIS2, DORA)
    - Required team certifications
    - Confidentiality and data protection requirements
    - Penalty clauses and SLAs"""
)

# Financial estimation agent
financial_analyst = Agent(
    name="financial-analyst",
    model="claude-haiku-4-5",
    system="""You estimate the financial impact of proposals:
    - Team cost based on profiles and dedication
    - Tool and license costs
    - Target margin and competitive pricing
    - Comparison with similar projects"""
)

@orchestrator(agents=[coordinator, tech_analyst,
                       compliance_analyst, financial_analyst])
async def analyze_rfp_complete(rfp_content: str) -> dict:
    """Complete RFP analysis flow with agent team."""
    # 1. Coordinator segments the tender
    segments = await coordinator.run(
        f"Segment this RFP into thematic blocks:\n{rfp_content}"
    )
    # 2. Each agent analyzes their segment in parallel
    tech_result = await tech_analyst.run(
        f"Analyze technical requirements:\n{segments['technical']}"
    )
    compliance_result = await compliance_analyst.run(
        f"Verify regulatory compliance:\n{segments['compliance']}"
    )
    financial_result = await financial_analyst.run(
        f"Estimate financial impact:\n{segments['financial']}"
    )
    # 3. Coordinator consolidates
    consolidated = await coordinator.run(
        f"""Consolidate these analyses into a go/no-go recommendation:
        Technical: {tech_result}
        Compliance: {compliance_result}
        Financial: {financial_result}"""
    )
    return consolidated
