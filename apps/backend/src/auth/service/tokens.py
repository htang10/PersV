from datetime import datetime, timedelta, timezone
from typing import Any, Union

from jose import jwt

from src.auth.config import auth_settings


def create_access_token(
    subject: Union[str, Any], expires_delta: int | None = None
) -> str:
    if expires_delta is not None:
        expire = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=auth_settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )

    payload = {
        "sub": subject,
        "type": "access",
        "exp": expire,
    }
    return jwt.encode(
        payload, auth_settings.JWT_SECRET_KEY, auth_settings.JWT_ALGORITHM
    )


def create_refresh_token(
    subject: Union[str, Any], expires_delta: int | None = None
) -> str:
    if expires_delta is not None:
        expire = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=auth_settings.JWT_REFRESH_TOKEN_EXPIRE_MINUTES
        )

    payload = {
        "sub": subject,
        "type": "refresh",
        "exp": expire,
    }
    return jwt.encode(
        payload, auth_settings.JWT_SECRET_KEY, auth_settings.JWT_ALGORITHM
    )


def decode_token(token: str) -> dict:
    return jwt.decode(
        token, auth_settings.JWT_SECRET_KEY, algorithms=[auth_settings.JWT_ALGORITHM]
    )
