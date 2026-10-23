"""Access tokens: short-lived, signed JWTs.

Access tokens are stateless. They are validated by signature and claims alone,
with no database lookup, so they cannot be revoked before they expire.
Their lifetime is therefore kept short.
"""

import uuid

import jwt
from jwt import InvalidTokenError

from src.auth.config import auth_settings
from src.auth.exceptions import InvalidAccessToken
from src.core.utils import get_current_datetime


def create_access_token(user_id: str) -> str:
    """Creates a short-lived, signed JWT access token for the given user.

    The token expires after ACCESS_TOKEN_EXP. It is signed, not encrypted, so
    anyone holding it can read its claims. Never put secrets in the payload.

    Claims:
        iss: Issuer, who created the token.
        sub: Subject, the user id.
        aud: Audience, who the token is intended for.
        exp: Expiry time.
        nbf: Not valid before this time.
        iat: Time of issue.
        jti: Unique token id.

    Args:
        user_id: ID of the user the token is issued for.

    Returns:
        The encoded JWT.
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
        payload=payload,
        key=auth_settings.JWT_SECRET_KEY,
        algorithm=auth_settings.JWT_ALGORITHM,
    )


def validate_access(access_token: str) -> dict:
    """Validates a JWT access token and returns its decoded claims.

    Validation is stateless: it does not check whether the subject still exists or is active.

    Args:
        access_token: The raw JWT string. Must be a non-empty string.

    Returns:
        The decoded JWT claims, including `sub` (the user id).

    Raises:
        InvalidAccessToken: If the token is malformed, expired, or fails any
            signature or claim check.
    """
    try:
        payload = jwt.decode(
            jwt=access_token,
            key=auth_settings.JWT_SECRET_KEY,
            algorithms=[auth_settings.JWT_ALGORITHM],
            audience=auth_settings.JWT_AUDIENCE,
            issuer=auth_settings.JWT_ISSUER,
        )
    except InvalidTokenError:
        raise InvalidAccessToken

    return payload
