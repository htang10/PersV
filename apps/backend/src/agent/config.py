from src.core.config import Settings


class AgentSettings(Settings):
    OPENAI_MODEL: str
    OPENAI_API_KEY: str


agent_settings = AgentSettings()  # type: ignore
