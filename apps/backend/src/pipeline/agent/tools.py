from langchain.tools import tool
from sqlalchemy import Engine, text
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
    engine: Engine, schema_summary: dict[str, dict[str, str]]
) -> tuple[list, str]:
    dialect = engine.dialect.name

    @tool
    def sql_execute(query: str) -> str:
        """Input to this tool is your generated SQL query.
        The tool validates, optimizes, and executes the query against the database.
        If the query contains errors or disallowed statements, an error message will be returned.
        If an error is returned, rewrite the query and try again.
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
                        return f"Disallowed statement: {type(node).__name__} is not allowed."

                if list(tree.find_all(exp.Star)):
                    return "Avoid SELECT * — specify only the columns needed."

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

    tools = [sql_execute]

    return tools, dialect
