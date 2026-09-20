from pydantic import BaseModel, Field


class HealthStatus(BaseModel):
    """A generic health status response."""

    status: str = Field()
