from pydantic import BaseModel, Field


class MessageResponse(BaseModel):
    """A generic message response."""

    message: str = Field()
