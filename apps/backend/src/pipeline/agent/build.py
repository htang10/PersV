from typing import Any

from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model

from src.core.utils import read_text_file
from src.pipeline.agent.tools import create_tools
from src.pipeline.config import pl_settings
from src.pipeline.schemas import QueryResponse

SYSTEM_PROMPT = read_text_file("system_prompt.txt")

model = init_chat_model(
    "openai:gpt-5.5",
    api_key=pl_settings.OPENAI_API_KEY,
    temperature=0,
    max_tokens=400,
    timeout=30,
)


def create_sql_agent(user_id: str | None, top_k: int = 5) -> Any:
    tools, dialect = create_tools(user_id, model=model)
    system_prompt = SYSTEM_PROMPT.format(dialect=dialect, top_k=top_k)
    return create_deep_agent(
        model=model,
        tools=tools,
        system_prompt=system_prompt,
        response_format=QueryResponse,
    )
