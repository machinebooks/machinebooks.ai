"""
Chapter 5: BaseModel pattern — audit fields, soft delete, multi-tenancy.

Every model in the Platform inherits from BaseModel, which provides:
- Automatic timestamps (created_at, updated_at)
- Soft delete via deleted_at (never physical DELETE on business data)
- created_by tracking for audit trail
- __bind_key__ support for multi-schema routing (operations_db, platform_core, analytics_db)

The Platform uses 3 MySQL schemas connected via SQLAlchemy multi-bind:
  - operations_db  (~50 models) — business data
  - platform_core  (~25 models) — users, roles, AI governance
  - analytics_db   (~15 models) — dashboards, intelligence
"""

import os
from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# =============================================================================
# Multi-bind configuration (Chapter 5)
# =============================================================================

DB_USER = os.environ.get("DB_USER", "plataforma")
DB_PASS = os.environ.get("DB_PASSWORD", "")
DB_HOST = os.environ.get("DB_HOST", "db")

SQLALCHEMY_DATABASE_URI = (
    f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:3306/operations_db"
    "?charset=utf8mb4"
)

SQLALCHEMY_BINDS = {
    "platform_core": (
        f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:3306/platform_core"
        "?charset=utf8mb4"
    ),
    "analytics_db": (
        f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:3306/analytics_db"
        "?charset=utf8mb4"
    ),
}

SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_size": 50,
    "max_overflow": 100,
    "pool_pre_ping": True,       # Avoids "MySQL has gone away"
    "pool_recycle": 3600,        # Recycle connections every hour
    "pool_timeout": 30,
}


# =============================================================================
# BaseModel mixin (Chapter 5)
# =============================================================================

class BaseModel(db.Model):
    """
    Abstract base for all Platform models.

    Provides audit timestamps and soft delete. Every business model
    inherits from this to ensure consistent audit trail across
    all 90+ SQLAlchemy models.
    """

    __abstract__ = True

    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime,
        onupdate=lambda: datetime.now(timezone.utc),
    )
    # Soft delete: NULL = active, datetime = deleted
    deleted_at = db.Column(db.DateTime, nullable=True)

    created_by = db.Column(db.Integer, nullable=True)  # FK to users.id

    # ------------------------------------------------------------------
    # Soft delete helpers
    # ------------------------------------------------------------------

    def soft_delete(self) -> None:
        """Mark record as deleted without physical DELETE."""
        self.deleted_at = datetime.now(timezone.utc)

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    def __repr__(self) -> str:
        cls = self.__class__.__name__
        pk = getattr(self, "id", "?")
        return f"<{cls} id={pk}>"
