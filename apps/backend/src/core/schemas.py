from pydantic import BaseModel, ConfigDict, Field


class CustomBaseModel(BaseModel):
    model_config = ConfigDict(
        str_min_length=1,
        str_strip_whitespace=True,
        extra="forbid",
        validate_default=True,
    )


class HealthStatus(CustomBaseModel):
    """A generic health status response."""

    status: str = Field()
