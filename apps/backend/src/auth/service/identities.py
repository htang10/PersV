import uuid

from fastapi import Response

from src.auth.config import auth_settings


def generate_anon_id() -> str:
    """Generates a cryptographically random anonymous ID."""
    return f"ANON{uuid.uuid4()}"


def is_valid_anon_id(value: str) -> bool:
    if not value.startswith("ANON"):
        return False

    try:
        uuid.UUID(value.removeprefix("ANON"))
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
        max_age=int(auth_settings.ANON_ID_EXP.total_seconds()),
        secure=True,
        httponly=True,
        samesite="strict",
    )
