from typing import Annotated

from pydantic import BaseModel, BeforeValidator, Field

NormalizedEmail = Annotated[str, BeforeValidator(lambda v: v.strip().lower())]


class MessageResponse(BaseModel):
    message: str = Field()


class OTPRequest(BaseModel):
    email: NormalizedEmail


class LoginRequest(BaseModel):
    email: NormalizedEmail
    code: str = Field(
        description="The 6-digit one-time password sent to the user's email.",
        pattern=r"^\d{6}$",
        examples=["123456"],
    )


class TokenResponse(BaseModel):
    token: str = Field(
        description="Short-lived JWT access token used for API authentication."
    )
    type: str = Field(
        default="Bearer",
        description="Authentication scheme used in the Authorization header.",
    )
