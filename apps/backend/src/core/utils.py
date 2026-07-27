from datetime import datetime, timezone
from pathlib import Path


def get_current_datetime() -> datetime:
    return datetime.now(timezone.utc)


def read_text_file(file_path: str | Path) -> str:
    return Path(file_path).read_text(encoding="utf-8")
