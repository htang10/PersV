from enum import StrEnum

from pydantic import BaseModel, Field

from src.core.types import NormalizedEmail


class MailingPurpose(StrEnum):
    LOGIN = "login"
    EMAIL_CHANGE = "email_change"
    ACCOUNT_DELETION = "account_deletion"

    @property
    def render(self) -> str:
        """Returns the value that will be rendered inside the email to be sent."""
        return {
            MailingPurpose.LOGIN: "sign-up/login",
            MailingPurpose.EMAIL_CHANGE: "email change",
            MailingPurpose.ACCOUNT_DELETION: "account deletion",
        }[self]


class OTPRequest(BaseModel):
    """Request payload for initiating OTP authentication.

    Attributes:
        email: The user's email address.
            Automatically validated and normalized.
    """

    email: NormalizedEmail = Field(description="The user's email address.")
    purpose: MailingPurpose = Field(description="The purpose of the OTP request.")


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


class SessionValidationResponse(BaseModel):
    """Response indicating whether the current authentication session is valid."""

    valid: bool = Field(
        description="Whether the current authentication session is valid."
    )


class EmailChangeRequest(BaseModel):
    new_email: NormalizedEmail = Field(description="The email address to switch to.")
    new_email_code: str = Field(
        description="The 6-digit one-time password sent to the new email address.",
        pattern=r"^\d{6}$",
        examples=["123456"],
    )
    current_email_code: str = Field(
        description="The 6-digit one-time password sent to the current email address the account is registered with.",
        pattern=r"^\d{6}$",
        examples=["123456"],
    )
