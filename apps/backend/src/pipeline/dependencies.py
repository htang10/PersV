from typing import Annotated

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session

from src.database import conn_manager
from src.pipeline.exceptions import ConnectionNotFoundError


def get_db():
    try:
        engine = conn_manager.get_engine()
    except ConnectionNotFoundError:
        raise HTTPException(
            status_code=401, detail="Invalid connection. Please reconnect."
        )

    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
