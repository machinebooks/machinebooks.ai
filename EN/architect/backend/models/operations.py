"""
Chapter 5: Operations domain models — operations_db schema.

Core business entities: Client, Project, Opportunity, Proposal.
These models represent the Platform's operational pipeline:
  Client -> Project -> Opportunity -> Proposal

Key patterns:
- Soft delete on all business models (deleted_at, never physical DELETE)
- Enum-based state machines (ProposalStatus, ProposalType)
- AI metadata fields on generated artifacts (ai_model_used, ai_generation_tokens)
- Composite indexes aligned with actual query patterns
"""

import enum
from datetime import datetime, timezone
from .base_model import db, BaseModel


# =============================================================================
# Enums (Chapter 5 + Chapter 9)
# =============================================================================

class ProposalType(enum.Enum):
    """Five proposal types reflecting different business scenarios."""
    BASE = "base"
    COMPETITIVE = "competitive"
    PREMIUM = "premium"
    CUSTOM = "custom"
    EXECUTIVE = "executive"


class ProposalStatus(enum.Enum):
    """
    Seven-state workflow for proposals.
    See Chapter 9 for the full state machine with allowed transitions.
    """
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SENT = "sent"
    WON = "won"
    LOST = "lost"


# =============================================================================
# Models
# =============================================================================

class Client(BaseModel):
    """Client entity — entry point of the business domain."""
    __tablename__ = "clients"
    # No __bind_key__ -> defaults to operations_db

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    sector = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    projects = db.relationship("Project", backref="client", lazy="dynamic")


class Project(BaseModel):
    """Project linked to a client. Generates opportunities and proposals."""
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(
        db.Integer, db.ForeignKey("clients.id"), nullable=False
    )
    name = db.Column(db.String(300), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    proposals = db.relationship("Proposal", backref="project", lazy="dynamic")


class Proposal(BaseModel):
    """
    Technical proposal generated for an opportunity.

    Chapter 5: AI metadata fields track which model generated the proposal
    and how many tokens it consumed, enabling per-proposal cost analysis
    without expensive JOINs against LLMUsageLog.
    """
    __tablename__ = "proposals"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(
        db.Integer, db.ForeignKey("projects.id"), nullable=False
    )
    opportunity_id = db.Column(
        db.Integer, db.ForeignKey("opportunities.id"), nullable=True
    )

    proposal_type = db.Column(
        db.Enum(ProposalType), nullable=False, default=ProposalType.BASE
    )
    status = db.Column(
        db.Enum(ProposalStatus), nullable=False, default=ProposalStatus.DRAFT
    )

    title = db.Column(db.String(300), nullable=False)
    executive_summary = db.Column(db.Text)

    # AI generation metadata — traceability of which model produced this
    ai_generated = db.Column(db.Boolean, default=False)
    ai_model_used = db.Column(db.String(100))          # e.g. claude-sonnet-4-6
    ai_generation_tokens = db.Column(db.Integer)       # consolidated total
    ai_generation_cost_eur = db.Column(db.Float)

    __table_args__ = (
        db.Index("idx_proposal_project_status", "project_id", "status"),
        db.Index("idx_proposal_type_created", "proposal_type", "created_at"),
    )


class Opportunity(BaseModel):
    """
    Business opportunity from external feeds (Chapter 13).
    Indexed in Meilisearch for full-text search (<10ms).
    """
    __tablename__ = "opportunities"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    source = db.Column(db.String(100))           # feed origin
    budget_amount = db.Column(db.Float)
    category = db.Column(db.String(100))
    deadline = db.Column(db.DateTime)
    external_id = db.Column(db.String(200), unique=True)
    relevance_score = db.Column(db.Float)        # 0-10, set by proactive alerts

    __table_args__ = (
        db.Index("idx_opp_category_deadline", "category", "deadline"),
    )
