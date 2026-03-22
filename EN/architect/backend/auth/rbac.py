"""
Chapter 6: RBAC multi-app — three-layer authorization pipeline.

Authorization flow (every protected endpoint):
  Layer 1: platform_guard  — verify JWT, extract claims, check against DB
  Layer 2: require_permission — check module.action against AppRole JSON
  Layer 3: rate_limit — sliding window in Redis (30/min REST, 10/min AI)

Key design decisions:
- Claims are ALWAYS verified against DB, never trusted from JWT alone
  (Claude's first version read is_admin from JWT claims — a critical bug)
- Permissions stored as JSON in AppRole for fine-grained control per module
- is_admin bypass per application (admin in 'operations' != admin in 'security')
- 4 apps: operations (6 roles), analytics (4), admin (3), security (3)
"""

from functools import wraps
from typing import Optional


# =============================================================================
# Layer 1: platform_guard (Chapter 6)
# =============================================================================

def platform_guard(f):
    """
    Verify JWT and extract user context from the DATABASE.

    CRITICAL: This decorator queries UserAppMembership on every request
    instead of trusting JWT claims. The performance cost (~1ms with Redis
    cache, 5-min TTL) is justified because:
      - A revoked user keeps access until token expires if we trust JWT
      - An attacker who forges a token with is_admin=True gets full access
      - Permission changes take effect immediately, not at next token refresh
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # In production, uses flask_jwt_extended:
        #   claims = get_jwt()
        #   current_user_id = get_jwt_identity()

        # Verify claims against DB — NEVER trust JWT alone
        # membership = db.session.query(UserAppMembership).join(
        #     App, UserAppMembership.app_id == App.id
        # ).filter(
        #     UserAppMembership.user_id == current_user_id,
        #     App.app_code == claims.get('app_code', 'operations'),
        #     UserAppMembership.is_active == True
        # ).first()

        # if not membership:
        #     audit_log('ACCESS_DENIED', severity='WARNING',
        #              details=f"No membership for user {current_user_id}")
        #     return jsonify({"error": "No access to this application"}), 403

        # Inject VERIFIED context — from DB, not from token
        # g.current_user_id = current_user_id
        # g.app_code = membership.app_code
        # g.user_role = membership.role.name
        # g.is_admin = membership.role.is_admin  # From DB, NEVER from JWT

        return f(*args, **kwargs)

    return decorated


# =============================================================================
# Layer 2: require_permission (Chapter 6)
# =============================================================================

def require_permission(module: str, action: str):
    """
    Verify that the user's role in the active application has
    permission for the requested action on the specified module.

    Usage:
        @require_permission('proposals', 'write')
        @require_permission('documents', 'upload')

    Permissions are stored as JSON in AppRole:
        {"clients": ["read", "write"], "proposals": ["read"]}
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # In production:
            # if g.is_admin:
            #     return f(*args, **kwargs)  # Admin bypass per-app
            #
            # permissions = get_user_permissions(g.current_user_id, g.app_code)
            # allowed_actions = permissions.get(module, [])
            #
            # if action not in allowed_actions:
            #     audit_log('ACCESS_DENIED', severity='WARNING',
            #              details=f"{module}.{action} denied")
            #     return jsonify({"error": "Insufficient permissions"}), 403

            return f(*args, **kwargs)

        return decorated
    return decorator


# =============================================================================
# Layer 3: rate_limit (Chapter 6)
# =============================================================================

def rate_limit(limit: int = 30, period: int = 60, scope: str = "user"):
    """
    Sliding window rate limiter backed by Redis.

    Differentiated limits (Chapter 6):
      - REST endpoints:  30 req/min
      - AI operations:   10 req/min (tokens cost money)
      - Login endpoint:   5 req/min (brute force prevention)

    Returns HTTP 429 with Retry-After header when exceeded.
    Redis-backed so it works across multiple backend instances.
    """
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # In production: check Redis sorted set with sliding window
            # key = f"rate:{scope}:{g.current_user_id}"
            # current_count = redis_client.zcard(key)
            # if current_count >= limit:
            #     return jsonify({"error": "Rate limit exceeded"}), 429
            return f(*args, **kwargs)

        return decorated
    return decorator


# =============================================================================
# Example: protected endpoint combining all 3 layers
# =============================================================================

# @proposals_bp.route('/api/proposals', methods=['POST'])
# @platform_guard                            # Layer 1: valid JWT, verified claims
# @require_permission('proposals', 'write')  # Layer 2: role has write permission
# @rate_limit(limit=30, period=60)           # Layer 3: 30 req/min sliding window
# def create_proposal():
#     """Create proposal — requires write permission on proposals module."""
#     data = request.get_json()
#     # g.current_user_id, g.app_code, g.user_role available
#     # ... business logic
