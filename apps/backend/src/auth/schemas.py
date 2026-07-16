from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field

NormalizedEmail = Annotated[str, BeforeValidator(lambda v: v.strip().lower())]


class OTPRequest(BaseModel):
    """Request payload for initiating an OTP (one-time password) flow.

    Attributes:
        email: The recipient's email address.
            Automatically stripped of leading/trailing whitespace and lowercased before validation.
    """

    email: NormalizedEmail


class OTPLoginRequest(BaseModel):
    """Request payload for OTP authentication."""

    email: NormalizedEmail
    code: str = Field(
        description="The 6-digit one-time password sent to the user's email.",
        pattern=r"^\d{6}$",
        examples=["123456"],
    )


class AuthResponse(BaseModel):
    """Authentication credentials issued by the server."""

    access_token: str = Field(
        description="Short-lived JWT access token used for API authentication."
    )
    token_type: str = Field(
        default="Bearer",
        description="Authentication scheme used in the Authorization header.",
    )
