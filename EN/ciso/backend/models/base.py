# Chapter 3 — BaseModel: the foundation of every GRC entity
#
# Every model in the platform inherits from this base, which enforces:
# - Multi-tenancy via corporate_id (mandatory, no default)
# - Full audit trail (created_by, updated_by, timestamps)
# - Soft delete (never physically remove compliance evidence)
# - Optimistic locking (prevent silent overwrites)
# - Public UUID (never expose internal numeric IDs)
# - Extensibility via extra_data JSON field

from sqlalchemy import (
    Column, BigInteger, String, Integer, Boolean, DateTime, JSON,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import func
from uuid import uuid4


class BaseModel(DeclarativeBase):
    """Base for all GRC models (~90+ entities).

    Guarantees multi-tenancy, complete audit trail, and soft delete
    across the entire platform without developer effort.
    """

    __abstract__ = True

    # --- Identification ---
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    uuid = Column(
        String(36), unique=True, nullable=False,
        default=lambda: str(uuid4()),
        comment="Public identifier for APIs — numeric id is never exposed",
    )

    # --- Multi-tenancy (mandatory) ---
    corporate_id = Column(
        Integer, nullable=False, index=True,
        comment=(
            "Tenant discriminator. EVERY query MUST filter by this field. "
            "A user from tenant A must never see data from tenant B. "
            "Missing this field is a security incident, not a bug."
        ),
    )

    # --- Audit trail ---
    created_at = Column(DateTime, server_default=func.now())
    created_by = Column(Integer, nullable=True, comment="User ID who created the record")
    updated_at = Column(DateTime, onupdate=func.now())
    updated_by = Column(Integer, nullable=True, comment="User ID who last modified the record")

    # --- Soft delete ---
    # In compliance, deleting evidence is worse than the non-compliance itself.
    is_deleted = Column(Boolean, default=False, index=True)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(Integer, nullable=True)

    # --- Optimistic locking ---
    # Prevents silent overwrites when two users edit the same record.
    # The second user gets HTTP 409 Conflict instead of losing the first user's changes.
    version = Column(Integer, default=1, nullable=False)

    # --- Extensibility ---
    # Per-tenant customizations without schema migrations.
    # Validated by Pydantic schemas in the application layer, not by the DB.
    extra_data = Column(JSON, nullable=True)
