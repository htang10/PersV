from pydantic import BaseModel, Field


class QueryResponse(BaseModel):
    """Response containing the query result and the generated SQL statement.

    Attributes:
        result (str): The result of the query.
        sql (str): The SQL query executed to obtain the result.
    """

    result: str = Field(description="The result of the query.")
    sql: str = Field(
        description="The SQL query that was generated and executed to get the result."
    )
