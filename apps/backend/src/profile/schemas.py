from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.core.types import NormalizedEmail


class UserProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    email: str = Field(description="The email address that the user registered with.")
    display_name: str = Field(description="The display name that the user set.")
    created_at: datetime = Field(
        description="The datetime that user created their account."
    )


class UserProfileUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    email: NormalizedEmail | None = Field(
        alias="new_email", default=None, description="New email address."
    )
    display_name: str | None = Field(
        alias="new_display_name",
        default=None,
        min_length=6,
        max_length=50,
        description="New display name. Length restrictions must be met.",
    )


class ProfileChangesResponse(BaseModel):
    updated_email: str | None = Field(
        default=None, description="Updated email address after reformatting."
    )
    updated_display_name: str | None = Field(
        default=None, description="Updated display name after reformatting."
    )
