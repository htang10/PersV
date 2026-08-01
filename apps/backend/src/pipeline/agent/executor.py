import ast
import logging
from typing import Any

from pipeline.exceptions import AgentError
from src.pipeline.agent.builder import create_sql_agent
from src.pipeline.database import custom_conn_manager

logger = logging.getLogger(__name__)


def generate_response(question: str, user_id: str | None) -> Any:
    """Generates a response to the provided question using the SQL agent.

    Raises:
        AgentError: If the agent fails during execution.
    """
    engine = custom_conn_manager.get_engine(user_id=user_id)
    schema = custom_conn_manager.get_schema(user_id=user_id)
    agent = create_sql_agent(engine=engine, schema=schema)

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
