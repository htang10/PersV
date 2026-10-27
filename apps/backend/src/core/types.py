from typing import Annotated

from pydantic import BeforeValidator, EmailStr


def _normalize_email(value: object) -> object:
    if isinstance(value, str):
        return value.strip().lower()
    return value  # non-strings fall through to EmailStr, which rejects them with a 422


NormalizedEmail = Annotated[EmailStr, BeforeValidator(lambda v: v.strip().lower())]
