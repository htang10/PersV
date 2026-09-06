import secrets
import uuid

from fastapi import Response
from fastapi.security import HTTPAuthorizationCredentials
from jose import JWTError, jwt

from src.auth.config import auth_settings
from src.auth.exceptions import InvalidToken
from src.core.redis_client import redis_client
from src.core.utils import get_current_datetime

REFRESH_TOKEN_EXP_SECONDS = int(auth_settings.REFRESH_TOKEN_EXP.total_seconds())


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


def create_refresh_token(user_id: str) -> str:
    """Creates a refresh token, an opaque random string, and stores it in Redis."""
    token = secrets.token_urlsafe(64)
    redis_client.setex(
        f"refresh_token:{token}",
        auth_settings.REFRESH_TOKEN_EXP,
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
