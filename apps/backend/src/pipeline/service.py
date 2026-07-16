import ast
import logging
from typing import Any

from src.auth.dependencies import auth_engine
from src.pipeline.agent import create_sql_agent
from src.pipeline.database import conn_manager
from src.pipeline.exceptions import AgentError

logger = logging.getLogger(__name__)


def generate_response(question: str) -> Any:
    """Generates a response using the SQL agent.

    Raises:
        AgentError: If the agent fails to process the question or generate a response.
    """
    agent = create_sql_agent()

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


def dispose_all_engines() -> None:
    conn_manager.disconnect()
    auth_engine.dispose()
