# Companion code for "The Cyber Range and the Machine" — Chapter 12
# Dynamic CTF flag generation and validation.
# This is STARTER code — not production-ready.
#
# Key security patterns:
# - HMAC-SHA256 for flag generation (deterministic per instance)
# - hmac.compare_digest for timing-safe comparison
# - Flag format: CYBERRANGE{hex_token}

import hashlib
import hmac
import os
import secrets
from datetime import datetime

FLAG_HMAC_SECRET = os.getenv("FLAG_HMAC_SECRET", "change-me-in-production").encode()
FLAG_PREFIX = os.getenv("FLAG_PREFIX", "CYBERRANGE")


def generate_flag(
    challenge_id: int,
    instance_id: int,
    salt: str | None = None,
) -> str:
    """
    Generate a unique, deterministic flag for a challenge instance.

    Chapter 12 explains the design:
    - Each instance gets a unique flag so players cannot share answers
    - HMAC ensures flags are verifiable without storing plaintext
    - The salt adds per-deployment randomness
    """
    if salt is None:
        salt = secrets.token_hex(8)

    message = f"{challenge_id}:{instance_id}:{salt}".encode()
    token = hmac.new(FLAG_HMAC_SECRET, message, hashlib.sha256).hexdigest()[:32]

    return f"{FLAG_PREFIX}{{{token}}}"


def hash_flag(flag: str) -> str:
    """
    Hash a flag for storage in the database.
    We store hashes, never plaintext flags.
    """
    return hashlib.sha256(flag.encode()).hexdigest()


def validate_flag(submitted: str, expected: str) -> bool:
    """
    Timing-safe flag comparison (Chapter 12: anti-timing-attack).

    Uses hmac.compare_digest instead of == to prevent timing
    side-channel attacks that could leak flag characters.
    """
    return hmac.compare_digest(submitted.strip(), expected.strip())


def validate_flag_by_hash(submitted: str, stored_hash: str) -> bool:
    """
    Validate a submitted flag against a stored SHA-256 hash.
    Useful when flags are stored as hashes in the database.
    """
    submitted_hash = hashlib.sha256(submitted.strip().encode()).hexdigest()
    return hmac.compare_digest(submitted_hash, stored_hash)


def calculate_dynamic_score(
    base_points: int,
    total_solves: int,
    min_points: int = 50,
    decay: float = 0.95,
) -> int:
    """
    Dynamic scoring: points decrease as more players solve the challenge.

    Chapter 12 covers the decay curve:
    - First solver gets full points
    - Each subsequent solve reduces the value
    - Floor ensures challenges always have some value
    """
    if total_solves <= 0:
        return base_points

    score = int(base_points * (decay ** total_solves))
    return max(score, min_points)


def format_flag_for_injection(flag: str) -> str:
    """
    Format a flag for injection into a VM via Ansible or cloud-init.

    Chapter 13 explains how flags are planted in VMs:
    - Written to /root/flag.txt (or C:\\flag.txt on Windows)
    - Embedded in service responses (web challenges)
    - Hidden in memory, registry, or logs (forensics challenges)
    """
    return f"echo '{flag}' > /root/flag.txt && chmod 400 /root/flag.txt"


def is_valid_flag_format(submitted: str) -> bool:
    """Quick format check before doing expensive validation."""
    return (
        submitted.startswith(f"{FLAG_PREFIX}{{")
        and submitted.endswith("}")
        and len(submitted) == len(FLAG_PREFIX) + 34  # prefix + { + 32 hex + }
    )
