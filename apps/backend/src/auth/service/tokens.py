import secrets
import uuid

from fastapi import Response
from fastapi.security import HTTPAuthorizationCredentials
from jose import JWTError, jwt

from src.auth.config import auth_settings
from src.auth.exceptions import InvalidAuthToken
from src.auth.utils import hash_credential
from src.core.redis_client import redis_client
from src.core.utils import get_current_datetime

REFRESH_TOKEN_EXP_SECONDS = int(auth_settings.REFRESH_TOKEN_EXP.total_seconds())


class RefreshTokenKey:
    """
    key: refresh_token:{hashed_refresh_token}
    value: user_id
    """

    PREFIX = "refresh_token"

    @classmethod
    def for_token(cls, token: str) -> str:
        return f"{cls.PREFIX}:{token}"


class SessionKey:
    """
    key: user_session:{user_id}
    values:
        - session_id1, created_at
        - session_id2, created_at
        ...
        - session_id5, created_at

    Each session id is a hashed refresh token
    """

    PREFIX = "user_session"

    @classmethod
    def for_user(cls, user_id: str) -> str:
        return f"{cls.PREFIX}:{user_id}"


def create_access_token(user_id: str) -> str:
    """Creates a short-lived, signed JWT access token for the given user.

    Standard claims (aud/iss/exp/nbf/iat/jti) are included so the token can be validated statelessly.
    """
    now = get_current_datetime()
    payload = {
        "iss": auth_settings.JWT_ISSUER,
        "sub": user_id,
        "aud": auth_settings.JWT_AUDIENCE,
        "exp": now + auth_settings.ACCESS_TOKEN_EXP,
        "nbf": now,
        "iat": now,
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(
        payload, auth_settings.JWT_SECRET_KEY, auth_settings.JWT_ALGORITHM
    )


def validate_access(credentials: HTTPAuthorizationCredentials | None) -> dict:
    """Validate a JWT access token and return its decoded claims.

    Args:
        credentials: Bearer token extracted from the Authorization header.

    Returns:
        The decoded JWT payload, or an empty dictionary if credentials are missing.

    Raises:
        InvalidToken: If the token is invalid, expired, or fails validation.
    """
    if not credentials:
        return {}

    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            auth_settings.JWT_SECRET_KEY,
            algorithms=[auth_settings.JWT_ALGORITHM],
            audience=auth_settings.JWT_AUDIENCE,
            issuer=auth_settings.JWT_ISSUER,
        )
    except JWTError:
        raise InvalidAuthToken

    return payload


def register_user_session(user_id: str, session_id: str) -> None:
    session_key = SessionKey.for_user(user_id)

    # Register the new session
    redis_client.zadd(
        name=session_key,
        mapping={
            session_id: get_current_datetime().timestamp()
        },  # Redis sorted set's scores are numeric
    )

    # Keep only the 3 newest sessions, clean up the rest
    old_sessions = redis_client.zrange(
        name=session_key,
        start=0,
        end=-(auth_settings.MAX_USER_SESSIONS + 1),
    )

    if old_sessions:
        redis_client.delete(
            *(RefreshTokenKey.for_token(token) for token in old_sessions)
        )
        redis_client.zrem(
            session_key,
            *old_sessions,
        )


def revoke_user_session(user_id: str, session_id: str) -> None:
    session_key = SessionKey.for_user(user_id)
    redis_client.zrem(
        session_key,
        session_id,
    )


def revoke_all_user_sessions(user_id: str) -> None:
    """Revokes every refresh token and session belonging to a user.

    Args:
        user_id: ID of the user whose sessions should all be revoked.
    """
    session_key = SessionKey.for_user(user_id)
    # Retrieve all refresh tokens user has using their id
    session_ids = redis_client.zrange(session_key, 0, -1)
    if not session_ids:
        return

    # Batch all the deletes into one single round-trip instead of N separate calls
    pipe = redis_client.pipeline()
    for session_id in session_ids:
        # First, delete all refresh tokens user has
        pipe.delete(RefreshTokenKey.for_token(session_id))
    # Finally delete all of their associated sessions
    pipe.delete(session_key)
    pipe.execute()


def create_refresh_token(user_id: str) -> str:
    """Creates a refresh token, an opaque random string, and stores it in Redis."""
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


def revoke_refresh_token(token: str) -> None:
    hashed_token = hash_credential(credential=token)
    key = RefreshTokenKey.for_token(hashed_token)
    user_id = redis_client.get(key)
    if user_id:
        redis_client.delete(key)
        revoke_user_session(
            user_id=user_id, session_id=hashed_token
        )  # The refresh token also serves as the session identifier.


def rotate_refresh_token(token: str) -> tuple[str, str]:
    """Rotates a refresh token and issues a new token pair.

    The existing refresh token is revoked before generating a new access
    token and refresh token.

    Raises:
        InvalidToken: If the refresh token is invalid or has been revoked.
    """
    hashed_token = hash_credential(credential=token)
    key = RefreshTokenKey.for_token(hashed_token)
    user_id = redis_client.get(key)
    if not user_id:
        raise InvalidAuthToken

    # invalidate old token immediately
    revoke_refresh_token(token=token)  # avoid double hashing

    # issue new pair
    new_access = create_access_token(user_id)
    new_refresh = create_refresh_token(user_id)

    return new_access, new_refresh


def set_refresh_token_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=REFRESH_TOKEN_EXP_SECONDS,
        secure=True,
        httponly=True,
        samesite="strict",
    )


def delete_refresh_token_cookie(response: Response) -> None:
    response.delete_cookie(
        key="refresh_token",
        secure=True,
        httponly=True,
        samesite="strict",
    )
