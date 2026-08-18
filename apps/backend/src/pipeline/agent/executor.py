import asyncio
import json
import logging
import time
from typing import Any

from anthropic import BadRequestError

from src.pipeline.agent.builder import create_sql_agent
from src.pipeline.database import custom_conn_manager
from src.pipeline.exceptions import AgentError
from src.pipeline.schemas import QueryResponse

logger = logging.getLogger(__name__)


async def generate_response(question: str, user_id: str | None) -> QueryResponse:
    """Generates a response to the provided question using the SQL agent.

    Raises:
        AgentError: If the agent fails during execution.
    """
    start = time.perf_counter()
    engine = custom_conn_manager.get_engine(user_id=user_id)
    schema = custom_conn_manager.get_schema(user_id=user_id)

    try:
        agent = create_sql_agent(engine=engine, schema=schema)
        stream = await agent.astream_events(
            input={"messages": [{"role": "user", "content": question}]},
            version="v3",
        )

        llm_calls, _ = await asyncio.gather(
            _consume_messages(stream), _consume_tool_calls(stream)
        )
        logger.info(f"Total LLM calls: {llm_calls}")

        output = await stream.output()
        return json.loads(output["messages"][-1].content[0]["text"])
    except BadRequestError as e:
        logger.error(f"Agent failed to generate response: {e}.")
        raise AgentError
    finally:
        elapsed = time.perf_counter() - start
        logger.info("Total execution time: %.3fs", elapsed)


async def _consume_messages(stream: Any) -> int:
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
