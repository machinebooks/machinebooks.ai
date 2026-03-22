# Extraído de: LibroCyberrange/cap-12-sistema-ctf.md
from sqlalchemy import (
    Column, Integer, String, Text, DateTime,
    Enum, ForeignKey, Boolean, JSON
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Challenge(Base):
    """Definición de un reto: qué hay que resolver."""
    __tablename__ = "challenge"

    id = Column(Integer, primary_key=True)
    title = Column(String(128))
    type = Column(Enum('ctf', 'crisis', 'guided', 'escape'))
    description = Column(Text)
    difficulty = Column(
        Enum('beginner', 'easy', 'medium', 'hard', 'extreme'),
        default='medium'
    )
    max_points = Column(Integer)
    status = Column(Enum('draft', 'published', 'archived'), default='draft')
    category = Column(String(64))        # web, crypto, forensics, pwn...
    tags = Column(JSON)                   # ["sqli", "blind", "mysql"]
    time_limit_minutes = Column(Integer)  # Límite opcional por participante
    max_attempts = Column(Integer)        # Intentos máximos de flag

    # --- Flags dinámicas ---
    flag_type = Column(Enum('static', 'dynamic'), default='static')
    template_vmid = Column(Integer)       # VMID del template en Proxmox
    template_type = Column(Enum('qemu', 'lxc'), default='lxc')
    setup_playbook_yaml = Column(Text)    # Playbook Ansible inline

    # Control operativo
    vm_ttl_hours = Column(Integer, default=2)
    auto_shutdown_on_flag = Column(Boolean, default=True)

    # Relación con MITRE ATT&CK
    mitre_techniques = relationship(
        "ChallengeMitreTechnique", back_populates="challenge"
    )


class ChallengeInstance(Base):
    """Ejecución de un reto por un usuario concreto."""
    __tablename__ = "challenge_instance"

    id = Column(Integer, primary_key=True)
    challenge_id = Column(Integer, ForeignKey("challenge.id"))
    user_id = Column(Integer, ForeignKey("user.id"))
    state = Column(Enum('open', 'done'), default='open')
    score = Column(Integer, default=0)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

    # --- Instancia de VM/CT para flags dinámicas ---
    vmid = Column(Integer)               # VMID de la instancia clonada
    vm_type = Column(Enum('qemu', 'lxc'))
    ip_address = Column(String(45))
    flag_value = Column(String(128))     # Flag única para este usuario
    hash_seed = Column(String(64))       # Seed criptográfico
    expires_at = Column(DateTime)
    vm_status = Column(String(20), default='none')


class CtfFlag(Base):
    """Flag individual dentro de un challenge."""
    __tablename__ = "ctf_flag"

    id = Column(Integer, primary_key=True)
    challenge_id = Column(Integer, ForeignKey("challenge.id"))
    flag_token = Column(String(64), unique=True)
    points = Column(Integer, default=100)
    clue = Column(Text)                  # Pista visible antes de empezar
    kind = Column(
        Enum('static', 'vm', 'container', 'dynamic'),
        default='static'
    )


class CtfCapture(Base):
    """Registro de captura: quién capturó qué flag y cuándo."""
    __tablename__ = "ctf_capture"

    id = Column(Integer, primary_key=True)
    instance_id = Column(Integer, ForeignKey("challenge_instance.id"))
    flag_id = Column(Integer, ForeignKey("ctf_flag.id"))
    user_id = Column(Integer, ForeignKey("user.id"))
    captured_at = Column(DateTime, default=datetime.utcnow)


class CtfHint(Base):
    """Pista asociada a una flag con penalización porcentual."""
    __tablename__ = "ctf_hint"

    id = Column(Integer, primary_key=True)
    flag_id = Column(Integer, ForeignKey("ctf_flag.id"))
    text = Column(Text)
    penalty_pct = Column(Integer, default=10)  # % de descuento
    order_idx = Column(Integer)                # Orden de revelación


class CtfHintUse(Base):
    """Registro de uso de pista por usuario."""
    __tablename__ = "ctf_hint_use"

    id = Column(Integer, primary_key=True)
    capture_id = Column(Integer, ForeignKey("ctf_capture.id"))
    hint_id = Column(Integer, ForeignKey("ctf_hint.id"))
    user_id = Column(Integer, ForeignKey("user.id"))
    instance_id = Column(Integer, ForeignKey("challenge_instance.id"))
    used_at = Column(DateTime, default=datetime.utcnow)
