from pydantic import Field

from src.core.schemas import CustomBaseModel


class QueryResponse(CustomBaseModel):
    """Response to a natural-language question about the database.

    Attributes:
        result: The answer, in plain language.
        sql: The SQL query that was executed. None if the question could not be answered.
        suggestions: Alternative questions to try. None if the question was answered.
    """

    result: str = Field(description="The answer to the question, in plain language.")
    sql: str | None = Field(
        default=None,
        description="The SQL query that was executed. None if the question could not be answered.",
    )
    suggestions: list[str] | None = Field(
        default=None,
        description="Alternative questions to try. Only present if no data could be retrieved.",
    )
