"""Refresh tokens: long-lived, opaque, revocable credentials.

Refresh tokens are stateful. Each is a random string checked against stored
state, and only its hash is kept, so it can be revoked at any time and a
leaked store does not expose usable tokens. Tokens are single-use: rotation
issues a new pair and invalidates the old token, with a short grace window
so concurrent requests do not end the session.
"""

import secrets
from typing import NamedTuple

from src.auth.config import auth_settings
from src.auth.exceptions import InvalidRefreshToken
from src.auth.service.tokens.access_tokens import create_access_token
from src.auth.service.tokens.keys import RefreshTokenKey, RotatedTokenKey
from src.auth.service.tokens.sessions import register_user_session, revoke_user_session
from src.auth.utils import hash_credential
from src.core.redis_client import redis_client

ROTATION_GRACE_SECONDS = 10
_ROTATE_SCRIPT = redis_client.register_script("""
local uid = redis.call('GETDEL', KEYS[1])
if uid then
    redis.call('SET', KEYS[2], uid, 'EX', ARGV[1])
    return {1, uid}
end
uid = redis.call('GET', KEYS[2])
if uid then
    return {2, uid}
end
return {0, ''}
""")


def create_refresh_token(user_id: str) -> str:
    """Creates a refresh token and registers it as the user's session.

    The token expires after `REFRESH_TOKEN_EXP`. Only its hash is stored, so
    the raw value is returned once and cannot be recovered later.

    Args:
        The ID of the user the token is issued for.

    Returns:
        The raw refresh token.
    """
    token = secrets.token_urlsafe(64)
    hashed_token = hash_credential(credential=token)

    redis_client.setex(
        RefreshTokenKey.for_token(hashed_token),
        auth_settings.REFRESH_TOKEN_EXP,
        user_id,
    )
    register_user_session(
        user_id=user_id,
        session_id=hashed_token,  # The refresh token also serves as the session identifier.
    )

    return token


def validate_refresh_token(token: str) -> bool:
    """Checks whether a refresh token is currently valid.

    Args:
        token: The raw refresh token to validate.

    Returns:
        True if the token is found, False otherwise.
    """
    _, _, user_id = _lookup_refresh_token(token=token)
    return bool(user_id)


def revoke_refresh_token(token: str) -> None:
    """Revokes a refresh token and ends its session.

    Does nothing if the token is unknown or already revoked.
    """
    hashed_token, key, user_id = _lookup_refresh_token(token=token)
    if user_id:
        redis_client.delete(key)
        revoke_user_session(
            user_id=user_id, session_id=hashed_token
        )  # The refresh token also serves as the session identifier.


class RotationResult(NamedTuple):
    """Outcome of a refresh token rotation.

    Attributes:
        user_id: ID of the user the token belongs to.
        access_token: The new access token. None if another request already
            rotated the token.
        refresh_token: The new refresh token. None if another request already
            rotated the token.
    """

    user_id: str
    access_token: str | None = None  # None if another request already rotated
    refresh_token: str | None = None


def rotate_refresh_token(token: str | None) -> RotationResult:
    """Rotates a refresh token, tolerating concurrent requests.

    The old token is invalidated on first use. Requests arriving within
    `ROTATION_GRACE_SECONDS` of that first use are still accepted, but receive
    no new tokens, since the first request's response already carries them.

    Args:
        token: The raw refresh token to rotate.

    Returns:
        A `RotationResult`. Its tokens are set only for the request that won
        the rotation.

    Raises:
        InvalidRefreshToken: If the token is missing, unknown, expired or revoked.
    """
    if not token:
        raise InvalidRefreshToken

    hashed_token = hash_credential(credential=token)
    key = RefreshTokenKey.for_token(hashed_token)

    outcome, user_id = _ROTATE_SCRIPT(
        keys=[key, RotatedTokenKey.for_token(hashed_token)],
        args=[ROTATION_GRACE_SECONDS],
    )
    if outcome == 0:
        raise InvalidRefreshToken
    if outcome == 2:
        return RotationResult(user_id=user_id)

    # Invalidate old token immediately
    revoke_user_session(user_id=user_id, session_id=hashed_token)
    return RotationResult(
        user_id=user_id,
        access_token=create_access_token(user_id),
        refresh_token=create_refresh_token(user_id),
    )


def _lookup_refresh_token(token: str) -> tuple[str, str, str | None]:
    """Hashes a refresh token and looks up its associated user id.

    Args:
        token: The raw refresh token to look up.

    Returns:
        A 3-tuple of:
            - The hashed token.
            - The key derived from the hashed token.
            - The associated user id, or None if the token is not found.
    """
    hashed_token = hash_credential(credential=token)
    key = RefreshTokenKey.for_token(hashed_token)
    return hashed_token, key, redis_client.get(key)
