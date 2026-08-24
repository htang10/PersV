from langchain.tools import tool
from sqlalchemy import Engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from sqlglot import exp, parse
from sqlglot.errors import OptimizeError, ParseError
from sqlglot.optimizer import optimize

# SQLAlchemy dialect names -> sqlglot dialect names
_DIALECT_MAP = {
    "postgresql": "postgres",
    "mariadb": "mysql",
    "mssql": "tsql",
}

_DISALLOWED_NODES = (
    exp.Insert,
    exp.Update,
    exp.Delete,
    exp.Drop,
    exp.Alter,
    exp.Create,
    exp.TruncateTable,
    exp.Merge,
)


def create_tools(
    engine: Engine, schema: str, schema_summary: dict[str, dict[str, str]]
) -> tuple[list, str]:
    dialect = engine.dialect.name

    @tool
    def get_distinct_values(table: str, column: str) -> str:
        """Inputs to this tool are:
            table: The exact table name to query, as listed in the schema.
            column: The exact column name within that table to sample values from.
        The tool returns a sample of distinct values for a column.
        Call this before filtering on a text, categorical, or boolean column, to see
        the actual values as they're stored (exact casing, spelling, abbreviations,
        or encoding) rather than guessing.
        DO NOT call this for purely numeric or date/time comparisons (e.g. ranges, greater-than/less-than),
        since those don't require verifying stored representations.
        If an error is returned, do not try to rerun this tool, instead move on.
        """
        # Model may pass a schema-qualified name (e.g. "app.table_name") since
        # it's instructed to qualify tables in SQL — normalize before validating.
        unqualified_table = table.split(".")[-1]
        if (
            unqualified_table not in schema_summary
            or column not in schema_summary[unqualified_table]
        ):
            return (
                f"Error: '{table}.{column}' is not a valid table/column in this schema."
            )

        # Quote schema and table names to ensure naming correctness and consistency
        preparer = engine.dialect.identifier_preparer
        qualified_table = (
            f"{preparer.quote(schema)}.{preparer.quote(unqualified_table)}"
            if schema
            else preparer.quote(unqualified_table)
        )
        quoted_column = preparer.quote(column)

        try:
            with Session(engine) as session:
                distinct_count = session.execute(
                    text(
                        f"SELECT COUNT(DISTINCT {quoted_column}) FROM {qualified_table}"
                    )
                ).scalar_one()

                if distinct_count == 0:
                    return "No values found."

                if distinct_count > 100:
                    return (
                        f"'{column}' has {distinct_count} distinct values — too many to "
                        f"list. Treat it as free text: use a pattern match (LIKE) instead "
                        f"of an exact-value filter."
                    )

                cap = 50
                result = session.execute(
                    text(
                        f"SELECT DISTINCT {quoted_column} FROM {qualified_table} ORDER BY {quoted_column} LIMIT :cap"
                    ),
                    {"cap": cap},
                )
                values = [row[0] for row in result]

            if distinct_count > cap:
                return (
                    f"Showing {cap} of {distinct_count} distinct values (not exhaustive, "
                    f"alphabetical sample): {values}"
                )
            return f"All {distinct_count} distinct values: {values}"
        except SQLAlchemyError as e:
            return f"Error retrieving distinct values: {e}"

    @tool
    def sql_execute(query: str) -> str:
        """Input to this tool is your generated SQL query.
        The tool validates, optimizes, and executes the query against the database.
        If the query contains errors or disallowed statements, an error message will be returned.
        If an error is returned, rewrite the query and try again.
        If the returned error is related to non-existent tables, user likely asked questions requiring
        data you do not have access to.
        """
        sqlglot_dialect = _DIALECT_MAP.get(dialect, dialect)

        try:
            trees = parse(query, sqlglot_dialect)
        except ParseError as e:
            return f"Syntax error: {e}"

        for tree in trees:
            if tree:
                for node in tree.walk():
                    if isinstance(node, _DISALLOWED_NODES):
                        return f"Query error: Disallowed statement: {type(node).__name__} is not allowed."

                if list(tree.find_all(exp.Star)):
                    return (
                        "Query error: Avoid SELECT * — specify only the columns needed."
                    )

                try:
                    optimized = optimize(
                        tree,
                        schema=schema_summary,
                        dialect=sqlglot_dialect,
                        quote_identifiers=False,
                        identify=False,
                    )
                    final_query = optimized.sql(dialect=sqlglot_dialect, pretty=True)
                except OptimizeError:
                    final_query = tree.sql(dialect=sqlglot_dialect, pretty=True)

                try:
                    with Session(engine) as session:
                        result = session.execute(text(final_query)).fetchall()
                    return str(result)
                except Exception as e:
                    return f"Query execution error: {e}"

        return "No valid query found."

    tools = [get_distinct_values, sql_execute]

    return tools, dialect
