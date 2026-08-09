from enum import StrEnum

from pydantic import BaseModel, Field


class MessageResponse(BaseModel):
    """A generic message response."""

    message: str = Field()


class HealthStatus(BaseModel):
    """A generic health status response."""

    status: str = Field()
