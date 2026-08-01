from langchain.tools import tool
from langchain_core.language_models import BaseChatModel
from sqlalchemy import Engine, inspect, text
from sqlalchemy.orm import Session


def create_tools(
    engine: Engine, schema: str | None, model: BaseChatModel
) -> tuple[list, str]:
    dialect = engine.dialect.name

    @tool
    def sql_list_tables() -> list[str]:
        """Input to this tool is an empty string, output is a comma-separated list of tables in the database.

        Always use this tool at start. MUST NOT skip!
        """
        inspector = inspect(engine)
        if schema:
            return inspector.get_table_names(schema=schema)
        return inspector.get_table_names()

    @tool
    def sql_check_query(query: str) -> str:
        """Use this to double-check if your query is correct before executing it.

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
            with Session(engine) as session:
                result = session.execute(text(query)).fetchall()
            return str(result)
        except Exception as e:
            return f"Error: {e}"

    tools = [sql_list_tables, sql_check_query, sql_run_query]

    return tools, dialect
