# Companion code for "The Cyber Range and the Machine" — Chapter 11
# Core SQLAlchemy 2.0 models (simplified). ~15 essential models.
# This is STARTER code — the real platform has ~90 models.

import enum
from datetime import datetime

from sqlalchemy import (
    Boolean, Column, DateTime, Enum, Float, ForeignKey,
    Integer, String, Text, UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


# -- Enums -----------------------------------------------------------------

class UserRole(str, enum.Enum):
    viewer = "viewer"
    player = "player"
    trainer = "trainer"
    operator = "operator"
    manager = "manager"
    admin = "admin"


class WorkzoneStatus(str, enum.Enum):
    pending = "pending"
    provisioning = "provisioning"
    running = "running"
    stopped = "stopped"
    destroying = "destroying"
    error = "error"


class ChallengeCategory(str, enum.Enum):
    web = "web"
    pwn = "pwn"
    crypto = "crypto"
    forensics = "forensics"
    reverse = "reverse"
    network = "network"
    misc = "misc"


class ChallengeDifficulty(str, enum.Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"
    insane = "insane"


# -- Users (Chapter 11 + Chapter 24) --------------------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(80), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.player, nullable=False)
    is_active = Column(Boolean, default=True)
    failed_login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    team_memberships = relationship("TeamMember", back_populates="user")
    score_logs = relationship("ScoreLog", back_populates="user")


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    color = Column(String(7), default="#0066FF")  # Hex color for UI
    created_at = Column(DateTime, default=datetime.utcnow)

    members = relationship("TeamMember", back_populates="team")


class TeamMember(Base):
    __tablename__ = "team_members"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    joined_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="team_memberships")
    team = relationship("Team", back_populates="members")

    __table_args__ = (UniqueConstraint("user_id", "team_id"),)


# -- Workzones (Chapter 8 + Chapter 10) -----------------------------------

class Workzone(Base):
    __tablename__ = "workzones"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(WorkzoneStatus), default=WorkzoneStatus.pending)
    vlan_id = Column(Integer, nullable=True, unique=True)
    network_cidr = Column(String(18), nullable=True)  # e.g. "10.100.1.0/24"
    ttl_minutes = Column(Integer, default=480)  # 8 hours default
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

    instances = relationship("ChallengeInstance", back_populates="workzone")


# -- Challenges & CTF (Chapter 12) ----------------------------------------

class Challenge(Base):
    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(Enum(ChallengeCategory), nullable=False)
    difficulty = Column(Enum(ChallengeDifficulty), nullable=False)
    points = Column(Integer, nullable=False, default=100)
    is_dynamic_scoring = Column(Boolean, default=False)
    template_id = Column(String(50), nullable=True)  # Proxmox template ID
    playbook = Column(String(255), nullable=True)     # Ansible playbook path
    max_instances = Column(Integer, default=10)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    flags = relationship("CtfFlag", back_populates="challenge")
    instances = relationship("ChallengeInstance", back_populates="challenge")


class CtfFlag(Base):
    """Static or dynamic flags for a challenge (Chapter 12)."""
    __tablename__ = "ctf_flags"

    id = Column(Integer, primary_key=True, autoincrement=True)
    challenge_id = Column(Integer, ForeignKey("challenges.id"), nullable=False)
    flag_hash = Column(String(128), nullable=False)  # SHA-256 of the flag value
    is_dynamic = Column(Boolean, default=True)
    points_override = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    challenge = relationship("Challenge", back_populates="flags")


class ChallengeInstance(Base):
    """A running instance of a challenge inside a workzone (Chapter 10)."""
    __tablename__ = "challenge_instances"

    id = Column(Integer, primary_key=True, autoincrement=True)
    challenge_id = Column(Integer, ForeignKey("challenges.id"), nullable=False)
    workzone_id = Column(Integer, ForeignKey("workzones.id"), nullable=False)
    proxmox_vmid = Column(Integer, nullable=True)
    ip_address = Column(String(15), nullable=True)
    status = Column(String(20), default="pending")
    dynamic_flag = Column(String(128), nullable=True)  # Unique flag for this instance
    started_at = Column(DateTime, nullable=True)
    destroyed_at = Column(DateTime, nullable=True)

    challenge = relationship("Challenge", back_populates="instances")
    workzone = relationship("Workzone", back_populates="instances")


# -- Scoring (Chapter 12) -------------------------------------------------

class ScoreLog(Base):
    """Records every flag submission attempt (Chapter 12)."""
    __tablename__ = "score_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    challenge_id = Column(Integer, ForeignKey("challenges.id"), nullable=False)
    submitted_flag = Column(String(255), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    points_awarded = Column(Integer, default=0)
    submitted_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="score_logs")

    __table_args__ = (
        # Prevent duplicate correct submissions
        UniqueConstraint("user_id", "challenge_id", "is_correct"),
    )


# -- Scenarios (Chapter 13 + Chapter 17) ----------------------------------

class Scenario(Base):
    """A pre-built or AI-generated exercise scenario."""
    __tablename__ = "scenarios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    difficulty = Column(Enum(ChallengeDifficulty), nullable=False)
    network_topology = Column(Text, nullable=True)   # JSON topology definition
    playbook_path = Column(String(255), nullable=True)
    mitre_techniques = Column(Text, nullable=True)    # Comma-separated ATT&CK IDs
    estimated_duration_min = Column(Integer, default=120)
    is_ai_generated = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


# -- Audit (Chapter 24) ---------------------------------------------------

class AuditLog(Base):
    """Immutable audit trail for security-relevant actions."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)      # e.g. "flag.submit", "vm.destroy"
    resource_type = Column(String(50), nullable=True)  # e.g. "workzone", "challenge"
    resource_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)              # JSON payload
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


# -- Coaching / AI interactions (Chapter 18) -------------------------------

class CoachingSession(Base):
    """Tracks AI coaching interactions per user per challenge."""
    __tablename__ = "coaching_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    challenge_id = Column(Integer, ForeignKey("challenges.id"), nullable=False)
    hints_given = Column(Integer, default=0)
    max_hints = Column(Integer, default=5)
    last_activity_at = Column(DateTime, default=datetime.utcnow)
    is_stalled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
