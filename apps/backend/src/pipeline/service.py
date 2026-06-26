import ast
import logging
from typing import Any

from src.pipeline.agent import create_sql_agent
from src.pipeline.exceptions import AgentError

logger = logging.getLogger(__name__)


def generate_response(question: str) -> Any:
    agent = create_sql_agent()

    try:
        stream = agent.stream_events(
            {"messages": [{"role": "user", "content": question}]},
            version="v3",
        )

        return ast.literal_eval(stream.output["messages"][-1].content[0]["text"])
    except Exception as e:
        logger.error(f"Agent failed to generate response: {e}.")
        raise AgentError
