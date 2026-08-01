from pathlib import Path
from typing import Any

from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model
from sqlalchemy import Engine

from src.core.utils import read_text_file
from src.pipeline.agent.tools import create_tools
from src.pipeline.config import pl_settings
from src.pipeline.schemas import QueryResponse

SYSTEM_PROMPT = read_text_file(Path(__file__).parent / "system_prompt.txt")


def create_sql_agent(engine: Engine, schema: str | None = None) -> Any:
    """Initializes a SQL agent tailored to the provided database connection.

    The agent is powered by GPT-5.5 and is configured to generate and execute read-only queries,
    returning structured respones in natural language.

    Args:
        engine: The SQLAlchemy engine representing the target database connection.
        schema: The schema to scope queries to. If None, the default schema is used.
    """
    model = init_chat_model(
        "openai:gpt-5.5",
        api_key=pl_settings.OPENAI_API_KEY,
        temperature=0.4,
        max_tokens=800,
        max_retries=3,
        timeout=30,
    )
    tools, dialect = create_tools(engine=engine, schema=schema, model=model)
    system_prompt = SYSTEM_PROMPT.format(dialect=dialect, top_k=5)
    return create_deep_agent(
        model=model,
        tools=tools,
        system_prompt=system_prompt,
        response_format=QueryResponse,
    )
