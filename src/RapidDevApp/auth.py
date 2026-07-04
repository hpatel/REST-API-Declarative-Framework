"""JWT authentication and permission checks."""

from __future__ import annotations

from .specs import AuthType


def apply_auth(ctx, auth_type: str):
    """Apply the configured auth mode.

    JWT mode uses flask-jwt-extended. The import is lazy so public/no-auth tests can
    import miniapi even when flask-jwt-extended is not installed.
    """

    if auth_type == AuthType.NONE:
        return

    if auth_type != AuthType.JWT:
        from flask import abort

        abort(500, description=f"Unsupported auth_type: {auth_type}")

    try:
        from flask_jwt_extended import get_jwt, get_jwt_identity, verify_jwt_in_request
    except ImportError as exc:
        raise RuntimeError(
            "auth_type='jwt' requires flask-jwt-extended. "
            "Install it with: pip install flask-jwt-extended"
        ) from exc

    verify_jwt_in_request()
    ctx.claims = get_jwt()
    ctx.user = get_jwt_identity()


def check_permissions(ctx, required_permissions: list[str]):
    """Check permission claims from the JWT payload."""

    if not required_permissions:
        return

    from flask import abort

    claims = ctx.claims or {}
    token_permissions = set(claims.get("permissions", []))
    required = set(required_permissions)
    missing = required - token_permissions

    if missing:
        abort(403, description=f"Missing permissions: {sorted(missing)}")
