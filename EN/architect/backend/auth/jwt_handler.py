"""
Chapter 6: JWT session management with Redis blocklist.

Key security decisions:
- Access tokens: 30 min TTL (short window if compromised)
- Refresh tokens: 8h normal / 24h trusted devices
- Blocklist in Redis with TTL = token lifetime (auto-cleanup)
- Claims verified against DB on every request (never trust JWT alone)
- Session invalidation: immediate on logout, password change, deactivation

WARNING: Claude generated the initial JWT code that looked correct but had
subtle vulnerabilities. The five real bugs found and fixed are documented
at the end of Chapter 6.
"""

import os
from datetime import datetime, timezone, timedelta
from functools import wraps
from typing import Optional

# Flask-JWT-Extended handles JWT creation and verification
# Redis stores the token blocklist for immediate revocation

JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "<YOUR_JWT_SECRET>")
JWT_ACCESS_EXPIRES = timedelta(
    seconds=int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES", 1800))
)
JWT_REFRESH_EXPIRES = timedelta(
    seconds=int(os.environ.get("JWT_REFRESH_TOKEN_EXPIRES", 28800))
)


# =============================================================================
# Token blocklist check (Chapter 6)
# =============================================================================

def is_token_revoked(jti: str, redis_client) -> bool:
    """
    Check if a token JTI is in the Redis blocklist.

    The blocklist uses Redis TTL equal to the token's remaining lifetime,
    so entries clean up automatically when the token would have expired anyway.
    This prevents the blocklist from growing indefinitely.
    """
    return redis_client.get(f"revoked_token:{jti}") is not None


# =============================================================================
# Session invalidation (Chapter 6)
# =============================================================================

def invalidate_user_sessions(
    user_id: int,
    jti: str,
    redis_client,
    db_session,
    reason: str = "manual_logout",
) -> None:
    """
    Invalidate all active sessions for a user.

    Called on: logout, password change, account deactivation.
    Two-phase approach:
      1. Add current access token JTI to Redis blocklist
      2. Mark all refresh tokens as revoked in the database
    """
    # Phase 1: Blocklist the current access token in Redis
    revocation_key = f"revoked_token:{jti}"
    redis_client.setex(
        revocation_key,
        int(JWT_ACCESS_EXPIRES.total_seconds()),
        "1",
    )

    # Phase 2: Revoke all refresh tokens in the database
    # UserSession model stores active refresh tokens per user
    db_session.execute(
        """
        UPDATE user_sessions
        SET is_active = FALSE,
            revoked_at = :now,
            revocation_reason = :reason
        WHERE user_id = :uid AND is_active = TRUE
        """,
        {
            "now": datetime.now(timezone.utc),
            "reason": reason,
            "uid": user_id,
        },
    )
    db_session.commit()

    # Audit trail (Chapter 6 — every security event is logged)
    _audit_log(
        "SESSION_INVALIDATED",
        user_id=user_id,
        severity="INFO",
        details=f"Reason: {reason}",
    )


# =============================================================================
# MFA verification (Chapter 6 — OTP via email)
# =============================================================================

def verify_mfa_code(
    user_id: int,
    code: str,
    redis_client,
) -> bool:
    """
    Verify a one-time MFA code sent via corporate email.

    The code is stored in Redis with a 5-minute TTL.
    After successful verification, the code is deleted to prevent reuse.

    Chapter 6: We chose email OTP over TOTP (Google Authenticator) for
    pragmatism — in a B2B environment where all users have corporate email
    already protected by the organization's identity system, the friction
    of configuring an authenticator app reduces adoption.
    """
    mfa_key = f"mfa_code:{user_id}"
    stored_code = redis_client.get(mfa_key)

    if stored_code is None:
        return False

    if stored_code.decode("utf-8") != code:
        return False

    # Delete after successful verification — one-time use
    redis_client.delete(mfa_key)
    return True


# =============================================================================
# Helpers
# =============================================================================

def _audit_log(
    action: str,
    user_id: Optional[int] = None,
    severity: str = "INFO",
    details: str = "",
) -> None:
    """
    Placeholder for the Platform's audit logging system.
    In production, this writes to the AuditLog table in platform_core
    with predefined actions: LOGIN_SUCCESS, ACCESS_DENIED,
    SESSION_INVALIDATED, SENSITIVE_DATA_ACCESS, etc.
    """
    pass  # See Chapter 6 for the full AuditLog model
