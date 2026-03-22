# Companion code for "The Cyber Range and the Machine" — Chapter 24
# JWT authentication + RBAC with 6 roles and account lockout.
# This is STARTER code — not production-ready.

import os
import time
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# -- Configuration ---------------------------------------------------------
JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXP_HOURS = int(os.getenv("JWT_EXP_HOURS", "4"))

# -- Role hierarchy (Chapter 24: six roles) --------------------------------
# Each role inherits permissions from the ones below it.
ROLES = {
    "viewer":     0,   # Read-only: dashboards, leaderboards
    "player":     1,   # Submit flags, access workzone VMs
    "trainer":    2,   # Create exercises, manage teams
    "operator":   3,   # Manage workzones, Proxmox operations
    "manager":    4,   # View analytics, audit logs
    "admin":      5,   # Full access: users, config, infrastructure
}

# -- Account lockout (Chapter 24: brute-force protection) ------------------
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_SECONDS = 900  # 15 minutes

# In-memory store for demo purposes. Use Redis or DB in production.
_failed_attempts: dict[str, list[float]] = {}


def check_lockout(username: str) -> None:
    """Raise 429 if the account has exceeded failed login attempts."""
    attempts = _failed_attempts.get(username, [])
    cutoff = time.time() - LOCKOUT_DURATION_SECONDS
    recent = [t for t in attempts if t > cutoff]
    _failed_attempts[username] = recent

    if len(recent) >= MAX_FAILED_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Account locked. Try again in {LOCKOUT_DURATION_SECONDS // 60} minutes.",
        )


def record_failed_attempt(username: str) -> None:
    """Record a failed login attempt for lockout tracking."""
    _failed_attempts.setdefault(username, []).append(time.time())


def clear_failed_attempts(username: str) -> None:
    """Reset failed attempts on successful login."""
    _failed_attempts.pop(username, None)


# -- Password hashing (bcrypt — Chapter 24) --------------------------------
def hash_password(plain: str) -> str:
    """Hash a plaintext password with bcrypt."""
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    return bcrypt.checkpw(plain.encode(), hashed.encode())


# -- JWT token creation and verification -----------------------------------
def create_token(user_id: int, username: str, role: str) -> str:
    """Create a signed JWT with user identity and role."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "username": username,
        "role": role,
        "iat": now,
        "exp": now + timedelta(hours=JWT_EXP_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> dict:
    """Decode and verify a JWT. Raises HTTPException on failure."""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


# -- FastAPI dependencies --------------------------------------------------
bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    """Extract and validate the current user from the Authorization header."""
    return verify_token(credentials.credentials)


def role_required(minimum_role: str):
    """
    Dependency factory: require a minimum role level.

    Usage in a router:
        @router.get("/admin-only", dependencies=[Depends(role_required("admin"))])
    """
    min_level = ROLES.get(minimum_role, 0)

    async def _check(user: dict = Depends(get_current_user)):
        user_level = ROLES.get(user.get("role", ""), -1)
        if user_level < min_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{minimum_role}' or higher required.",
            )
        return user

    return _check
