import secrets
import uuid
from datetime import timedelta

from fastapi.security import HTTPAuthorizationCredentials
from jose import JWTError, jwt

from core.utils import get_current_datetime
from src.auth.config import auth_settings
from src.auth.exceptions import InvalidToken
from src.core.redis import redis_client


def create_access_token(user_id: str) -> str:
    now = get_current_datetime()
    payload = {
        "iss": auth_settings.JWT_ISSUER,
        "sub": user_id,
        "aud": auth_settings.JWT_AUDIENCE,
        "exp": now + timedelta(minutes=auth_settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        "nbf": now,
        "iat": now,
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(
        payload, auth_settings.JWT_SECRET_KEY, auth_settings.JWT_ALGORITHM
    )


def create_refresh_token(user_id: str) -> str:
    token = secrets.token_urlsafe(64)
    redis_client.setex(
        f"refresh_token:{token}",
        timedelta(minutes=auth_settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES),
        user_id,
    )
    return token


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
        raise InvalidToken

    return payload


def revoke_refresh_token(token: str) -> None:
    redis_client.delete(f"refresh_token:{token}")


def rotate_refresh_token(old_token: str) -> tuple[str, str]:
    """Rotates a refresh token and issues a new token pair.

    The existing refresh token is revoked before generating a new access
    token and refresh token.

    Raises:
        InvalidToken: If the refresh token is invalid or has been revoked.
    """
    user_id = redis_client.get(f"refresh_token:{old_token}")

    if not user_id:
        raise InvalidToken

    # invalidate old token immediately
    revoke_refresh_token(old_token)

    # issue new pair
    new_access = create_access_token(user_id)
    new_refresh = create_refresh_token(user_id)

    return new_access, new_refresh
