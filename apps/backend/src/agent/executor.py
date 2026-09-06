import asyncio
import logging
import time
from typing import Any

from anthropic import BadRequestError

from src.agent.schemas import QueryResponse
from src.pipeline.database import custom_conn_manager
from src.pipeline.exceptions import AgentError, ConnectionNotFoundError

logger = logging.getLogger(__name__)


async def generate_response(question: str, user_id: str) -> QueryResponse:
    """Generates a response to the provided question using the SQL agent.

    Streams the agent's execution, logging each LLM message and tool call as
    they arrive, then returns the final structured response.

    Args:
        question: The user's prompt.
        user_id: ID of the user issuing the prompt, used to look up their
            agent connection.

    Returns:
        The agent's structured response to the question.

    Raises:
        AgentError: Either the agent fails during execution or
            no connection associated with the provided ID was found.
    """
    start = time.perf_counter()

    try:
        agent = custom_conn_manager.get_agent(user_id=user_id)
        stream = await agent.astream_events(
            input={"messages": [{"role": "user", "content": question}]},
            version="v3",
        )

        llm_calls, _ = await asyncio.gather(
            _consume_messages(stream), _consume_tool_calls(stream)
        )
        logger.info(f"Total LLM calls: {llm_calls}")

        output = await stream.output()
        return output["structured_response"]
    except (BadRequestError, ConnectionNotFoundError) as e:
        logger.error(f"Agent failed to generate response: {e}.")
        raise AgentError
    finally:
        elapsed = time.perf_counter() - start
        logger.info("Total execution time: %.3fs", elapsed)


async def _consume_messages(stream: Any) -> int:
    """Consumes and logs each LLM message from the agent event stream.

    Returns:
        The number of LLM messages consumed.
    """
    llm_calls = 0
    async for message in stream.messages:
        full_message = await message.output
        logger.info(
            {
                "Message": await message.text,
                "Token usage": full_message.usage_metadata,
            }
        )
        llm_calls += 1
    return llm_calls


async def _consume_tool_calls(stream: Any) -> None:
    """Consumes and logs each tool call from the agent event stream."""
    async for call in stream.tool_calls:
        async for delta in call.output_deltas:
            print(delta, end="", flush=True)
        logger.info(
            {
                "Tool call": call.tool_name,
                "Input": call.input,
                "Output": call.output,
                "Error": call.error,
            }
        )
