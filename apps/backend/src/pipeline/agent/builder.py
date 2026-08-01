import ast
import logging
from pathlib import Path
from typing import Any, Sequence

from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model

from pipeline.database import DEMO_ENGINE, custom_conn_manager
from src.core.utils import read_text_file
from src.pipeline.agent.tools import create_tools
from src.pipeline.config import pl_settings
from src.pipeline.exceptions import AgentError
from src.pipeline.schemas import QueryResponse

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = read_text_file(Path(__file__).parent / "system_prompt.txt")


def _create_sql_agent(engine: Engine, schema: str | None = None, top_k: int = 5) -> Any:
    model = init_chat_model(
        "openai:gpt-5.5",
        api_key=pl_settings.OPENAI_API_KEY,
        temperature=0,
        max_tokens=400,
        timeout=30,
    )
    tools, dialect = create_tools(engine=engine, schema=schema, model=model)
    system_prompt = SYSTEM_PROMPT.format(dialect=dialect, top_k=top_k)
    return create_deep_agent(
        model=model,
        tools=tools,
        system_prompt=system_prompt,
        response_format=QueryResponse,
    )


def generate_response(question: str, user_id: str | None) -> Any:
    """Generates a response to the provided question using the SQL agent.

    Raises:
        AgentError: If the agent fails during execution.
    """
    engine = custom_conn_manager.get_engine(user_id=user_id)
    schema = custom_conn_manager.get_schema(user_id=user_id) if user_id else None
    agent = _create_sql_agent(engine=engine, schema=schema)

    try:
        stream = agent.stream_events(
            {"messages": [{"role": "user", "content": question}]},
            version="v3",
        )

        for kind, item in stream.interleave("messages", "tool_calls"):
            if kind == "messages":
                logger.debug(f"Agent message: {item.text}")
            elif kind == "tool_calls":
                logger.debug(f"\nTool call: {item.tool_name}({item.input})")
                for delta in item.output_deltas:
                    logger.debug(delta)
                logger.debug(f"\nTool result: {item.output}")

        return ast.literal_eval(stream.output["messages"][-1].content[0]["text"])
    except Exception as e:
        logger.error(f"Agent failed to generate response: {e}.")
        raise AgentError
    finally:
        if engine is not DEMO_ENGINE:
            engine.dispose()
