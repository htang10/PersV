import json
from pathlib import Path

from langchain.agents import create_agent
from langchain_anthropic import ChatAnthropic
from langgraph.graph.state import CompiledStateGraph
from sqlalchemy import Engine, inspect

from src.agent.schemas import QueryResponse
from src.agent.tools import create_tools
from src.core.utils import read_text_file
from src.pipeline.config import pl_settings

SYSTEM_PROMPT = read_text_file(Path(__file__).parent / "system_prompt.txt")

model = ChatAnthropic(
    model=pl_settings.ANTHROPIC_MODEL,
    anthropic_api_key=pl_settings.ANTHROPIC_API_KEY,
    temperature=0.1,
    max_retries=3,
    default_request_timeout=30,
)


def create_sql_agent(engine: Engine, schema: str) -> CompiledStateGraph:
    """Initializes a SQL agent tailored to the provided database connection.

    The agent is configured to generate and execute read-only queries, returning structured responses in natural language.

    Args:
        engine: SQLAlchemy engine connected to the target database.
        schema: The schema to scope queries to.
    """
    schema_summary = _build_schema_summary(engine=engine, schema=schema)
    tools, dialect = create_tools(
        engine=engine, schema=schema, schema_summary=schema_summary
    )
    system_prompt = SYSTEM_PROMPT.format(
        dialect=dialect,
        top_k=5,
        schema_name=schema or "default",
        schema_summary=json.dumps(schema_summary),
    )
    return create_agent(
        model=model,
        tools=tools,
        system_prompt=system_prompt,
        response_format=QueryResponse,
    )


def _build_schema_summary(engine: Engine, schema: str) -> dict[str, dict[str, str]]:
    """Inspects the database schema and build a mapping of tables to their columns and types.

    Args:
        engine: SQLAlchemy engine connected to the target database.
        schema: Name of the database schema to inspect.

    Returns:
        A dict mapping each table name to a dict of its column names and
        SQL types.
    """
    inspector = inspect(engine)

    result = {}
    for table in inspector.get_table_names(schema=schema):
        columns = inspector.get_columns(table, schema=schema)
        result[table] = {column["name"]: str(column["type"]) for column in columns}
    return result
