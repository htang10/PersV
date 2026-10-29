from src.core.config import Settings


class AgentSettings(Settings):
    OPENAI_MODEL: str = "gpt-5.6-luna"
    OPENAI_API_KEY: str


agent_settings = AgentSettings()  # type: ignore
