"""
Chapter 9: Proposal state machine and business service routes.

The Platform supports 5 proposal types (base, competitive, premium,
custom, executive) with a 7-state workflow:

    DRAFT -> IN_REVIEW -> APPROVED -> SENT -> WON
                       -> REJECTED         -> LOST

Key patterns:
- Explicit transition map (no arbitrary state jumps)
- Each transition triggers audit logging
- AI-assisted generation tracked with model + token metadata
- Export to multiple formats: PDF, DOCX, PPTX
"""

from datetime import datetime, timezone
from typing import Optional


# =============================================================================
# State machine transitions (Chapter 9)
# =============================================================================

ALLOWED_TRANSITIONS = {
    "draft":     ["in_review"],
    "in_review": ["approved", "rejected"],
    "approved":  ["sent"],
    "rejected":  ["draft"],           # Can be reworked
    "sent":      ["won", "lost"],
    "won":       [],                  # Terminal state
    "lost":      [],                  # Terminal state
}


def validate_transition(current_status: str, new_status: str) -> bool:
    """
    Validate that a status transition is allowed.

    Chapter 9: Explicit transition map prevents arbitrary state jumps.
    A proposal cannot go from DRAFT directly to SENT — it must pass
    through IN_REVIEW and APPROVED first.
    """
    allowed = ALLOWED_TRANSITIONS.get(current_status, [])
    return new_status in allowed


# =============================================================================
# Proposal service (Chapter 9)
# =============================================================================

class ProposalService:
    """
    Business logic for proposal management.

    Handles state transitions, AI-assisted generation, and export.
    Each operation is audited and respects RBAC permissions.
    """

    def transition_status(
        self,
        proposal_id: int,
        new_status: str,
        user_id: int,
    ) -> dict:
        """
        Transition a proposal to a new status with validation.

        Returns dict with success/error information.
        Every transition is logged to the audit trail.
        """
        # In production: fetch proposal from DB
        # proposal = Proposal.query.get_or_404(proposal_id)
        # current = proposal.status.value

        current = "draft"  # Placeholder

        if not validate_transition(current, new_status):
            return {
                "error": f"Transition {current} -> {new_status} not allowed",
                "allowed": ALLOWED_TRANSITIONS.get(current, []),
            }

        # Update status
        # proposal.status = ProposalStatus(new_status)
        # proposal.updated_at = datetime.now(timezone.utc)
        # db.session.commit()

        # Audit trail
        # audit_log('PROPOSAL_STATUS_CHANGED', user_id=user_id,
        #          details=f"Proposal {proposal_id}: {current} -> {new_status}")

        return {"success": True, "new_status": new_status}

    def generate_with_ai(
        self,
        project_id: int,
        proposal_type: str,
        user_id: int,
        model: str = "claude-sonnet-4-6",
    ) -> dict:
        """
        Generate a proposal draft using Claude.

        Chapter 9 + Chapter 14: The AI service analyzes requirements,
        searches for relevant team profiles and products, then generates
        a structured proposal. With Universal Tools (Chapter 14), this
        takes ~102 seconds vs 5+ minutes with the old 19-tool approach.

        AI metadata (model, tokens, cost) is stored on the Proposal
        record for per-proposal cost analysis (Chapter 5).
        """
        # 1. Fetch project context
        # project = Project.query.get_or_404(project_id)

        # 2. Call AI service for generation
        # response = ai_service.generate_proposal(
        #     project_context=project.to_context_dict(),
        #     proposal_type=proposal_type,
        #     model=model,
        # )

        # 3. Create proposal with AI metadata
        # proposal = Proposal(
        #     project_id=project_id,
        #     proposal_type=ProposalType(proposal_type),
        #     status=ProposalStatus.DRAFT,
        #     title=response.title,
        #     executive_summary=response.summary,
        #     ai_generated=True,
        #     ai_model_used=model,
        #     ai_generation_tokens=response.total_tokens,
        #     ai_generation_cost_eur=response.cost_eur,
        #     created_by=user_id,
        # )
        # db.session.add(proposal)
        # db.session.commit()

        return {
            "proposal_id": 1,  # Placeholder
            "status": "draft",
            "ai_generated": True,
            "model_used": model,
        }


# =============================================================================
# Route definitions (Chapter 9 — Flask blueprint)
# =============================================================================

# In production, these are Flask blueprint routes:
#
# @proposals_bp.route('/api/proposals', methods=['POST'])
# @platform_guard
# @require_permission('proposals', 'write')
# @rate_limit(limit=30, period=60)
# def create_proposal():
#     data = request.get_json()
#     service = ProposalService()
#     return jsonify(service.generate_with_ai(
#         project_id=data['project_id'],
#         proposal_type=data.get('type', 'base'),
#         user_id=g.current_user_id,
#     ))
#
# @proposals_bp.route('/api/proposals/<int:pid>/status', methods=['PATCH'])
# @platform_guard
# @require_permission('proposals', 'write')
# def update_status(pid):
#     data = request.get_json()
#     service = ProposalService()
#     result = service.transition_status(pid, data['status'], g.current_user_id)
#     if 'error' in result:
#         return jsonify(result), 400
#     return jsonify(result)
