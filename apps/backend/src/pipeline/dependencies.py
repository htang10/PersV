from typing import Annotated, Any, Generator

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from src.pipeline.database import conn_manager
from src.pipeline.exceptions import ConnectionNotFoundError


def get_db() -> Generator[Session, Any, None]:
    try:
        engine = conn_manager.get_engine()
    except ConnectionNotFoundError:
        raise HTTPException(
            status_code=401,
            detail="Invalid connection. Please reconnect.",
        )

    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
