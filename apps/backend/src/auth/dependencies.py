from typing import Annotated, Any, Generator

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.config import settings

auth_engine = create_engine(str(settings.DATABASE_URL))


def get_auth_db() -> Generator[Session, Any, None]:
    with Session(auth_engine) as session:
        yield session


AuthSessionDep = Annotated[Session, Depends(get_auth_db)]
