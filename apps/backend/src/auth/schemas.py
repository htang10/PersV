from typing import Annotated

from pydantic import BaseModel, BeforeValidator, EmailStr, Field

NormalizedEmail = Annotated[EmailStr, BeforeValidator(lambda v: v.strip().lower())]


class OTPRequest(BaseModel):
    """Request payload for initiating OTP authentication.

    Attributes:
        email: The user's email address.
            Automatically validated and normalized.
    """

    email: NormalizedEmail = Field(description="The user's email address.")


class OTPResponse(BaseModel):
    """Response returned after an OTP code is generated and sent.

    Attributes:
        to: The recipient's email address. Included for confirmation only.
        expires_in: The number of seconds until the OTP code expires.
    """

    to: NormalizedEmail = Field(
        description="The email address to which the OTP code will be sent."
    )
    expires_in: int = Field(description="Seconds until the OTP code expires.")


class OTPLoginRequest(BaseModel):
    """Request payload for completing OTP authentication.

    Attributes:
        email: The user's email address.
            Automatically validated and normalized.
        code: The 6-digit one-time password sent to the user's email.
    """

    email: NormalizedEmail = Field(description="The user's email address.")
    code: str = Field(
        description="The 6-digit one-time password sent to the user's email.",
        pattern=r"^\d{6}$",
        examples=["123456"],
    )


class AuthResponse(BaseModel):
    """Authentication credentials issued by the server.

    Attributes:
        token: Short-lived JWT access token used for API authentication.
        type: Authentication scheme used in the Authorization header.
    """

    token: str = Field(
        description="Short-lived JWT access token used for API authentication."
    )
    type: str = Field(
        default="Bearer",
        description="Authentication scheme used in the Authorization header.",
    )
