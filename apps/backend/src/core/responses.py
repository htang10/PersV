from typing import Any, Mapping

from fastapi.responses import JSONResponse
from starlette.background import BackgroundTask


class APIResponse(JSONResponse):
    def __init__(
        self,
        content: Any = None,
        metadata: Mapping[str, str] | None = None,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
    ) -> None:
        self.metadata = metadata
        super().__init__(
            content=content,
            status_code=status_code,
            headers=headers,
            media_type=media_type,
            background=background,
        )

    def render(self, content: Any) -> bytes:
        envelope = {
            "data": content,
            "metadata": self.metadata,
        }
        return super().render(envelope)
