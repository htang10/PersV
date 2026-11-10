import logging
import uuid
from typing import Annotated

from fastapi import Cookie, Depends, Request, Response

from src.connection.config import conn_settings
from src.core.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)
anon_id_rl = RateLimiter("anon", conn_settings.ANON_ID_LIMITS)


def generate_anon_id() -> str:
    """Generates a cryptographically random anonymous ID."""
    return f"ANON{uuid.uuid4()}"


def is_valid_anon_id(anon_id: str) -> bool:
    if not anon_id.startswith("ANON"):
        return False

    try:
        uuid.UUID(anon_id.removeprefix("ANON"))
        return True
    except ValueError:
        return False


def set_anon_id_cookie(response: Response, anon_id: str) -> None:
    """Sets the anonymous user id as browser cookie for anonymous users.

    This function can alo be used to reset the expiry time of an existing anonymous id.
    """
    response.set_cookie(
        key="anon_id",
        value=anon_id,
        max_age=int(conn_settings.CONN_EXP.total_seconds()),
        secure=True,
        httponly=True,
        samesite="strict",
    )


def get_user_id(
    request: Request,
    response: Response,
    anon_id: str | None = Cookie(default=None, include_in_schema=False),
) -> str:
    if anon_id and is_valid_anon_id(anon_id):
        # Reset the expiration whenever an existing anonymous id is reused
        set_anon_id_cookie(response=response, anon_id=anon_id)
        return anon_id

    # If no id was found in browser cookie, generate a new one
    new_anon_id = generate_anon_id()
    set_anon_id_cookie(response, anon_id=new_anon_id)

    # Rate limit on the number of anon ids generated per IP address
    anon_id_rl.consume(ip=request.client.host)
    return new_anon_id


UserId = Annotated[str, Depends(get_user_id)]
