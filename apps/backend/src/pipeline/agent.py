from typing import Any

from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.core.config import settings
from src.database import conn_manager
from src.pipeline.schemas import QueryResponse

model = init_chat_model(
    "openai:gpt-5.5",
    api_key=settings.OPENAI_API_KEY,
    temperature=0,
    max_tokens=400,
    timeout=30,
)


@tool
def sql_list_tables() -> list[str]:
    """Return a comma-separated list of table names (e.g. "users, orders, products")."""

    return conn_manager.get_tables()


@tool
def sql_check_query(query: str) -> str:
    """Double check if your query is correct before executing it.

    Always use this tool before executing a query with `sql_run_query`.
    """

    checking_prompt = """
    ```
    {query}
    ```

    **Correctness**
    - Using NOT IN with NULL values (use NOT EXISTS instead)
    - Using UNION when UNION ALL should have been used
    - Using BETWEEN for exclusive ranges
    - Data type mismatch in predicates
    - Using the correct number of arguments for functions
    - Casting to the correct data type
    - Using the proper columns for joins
    - Filtering on aggregated values with WHERE instead of HAVING
    - Referencing a column alias in the same SELECT clause that defines it
    - Using column positions in ORDER BY that don't match the SELECT list

    **Completeness**
    - Missing GROUP BY columns (every non-aggregated column in SELECT must appear in GROUP BY)
    - Missing join conditions that produce a cartesian product
    - Overly broad WHERE clauses that match more rows than intended

    **Safety**
    - Queries that modify data (INSERT, UPDATE, DELETE, DROP, TRUNCATE, ALTER) — only SELECT statements are permitted
    - Referencing tables or columns that do not exist in the provided schema

    **Style & portability**
    - Properly quoting identifiers that are reserved words or contain special characters
    - Using database-specific functions where a portable equivalent exists

    If there are any of the above mistakes, rewrite the query to fix them.
    If there are no mistakes, reproduce the original query exactly.

    Output the final SQL query only, with no explanation or markdown formatting.

    SQL Query:
    """.format(query=query)

    response = model.invoke(checking_prompt)
    return response.text.strip()


@tool
def sql_run_query(query: str) -> str:
    """Run a SQL query and return the result.

    If the query is not correct, an error message will be returned.
    If an error is returned, rewrite the query, check the query, and try again.

    Args:
        query: A detailed and correct SQL query that answers user's question.

    Returns:
        The result of the SQL query after successful execution.
    """

    try:
        with Session(conn_manager.get_engine()) as session:
            result = session.execute(text(query)).fetchall()
        return str(result)
    except Exception as e:
        return f"Error: {e}"


tools = [sql_list_tables, sql_check_query, sql_run_query]

SYSTEM_PROMPT = """
You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct {dialect} query to run,
then look at the results of the query and return the answer. Unless the user
specifies a specific number of examples they wish to obtain, always limit your
query to at most {top_k} results.

You can order the results by a relevant column to return the most interesting
examples in the database. Never query for all the columns from a specific table,
only ask for the relevant columns given the question.

You MUST double check your query before executing it. If you get an error while
executing a query, rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the
database.

To start you should ALWAYS look at the tables in the database to see what you
can query. Do NOT skip this step.

Then you should query the schema of the most relevant tables.
"""


def create_sql_agent(top_k: int = 5) -> Any:
    dialect = conn_manager.get_dialect()
    system_prompt = SYSTEM_PROMPT.format(dialect=dialect, top_k=top_k)
    return create_deep_agent(
        model=model,
        tools=tools,
        system_prompt=system_prompt,
        response_format=QueryResponse,
    )
