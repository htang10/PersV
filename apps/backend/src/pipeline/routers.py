from typing import Annotated

from fastapi import Form, HTTPException, status
from fastapi.routing import APIRouter

from src.config import settings
from src.database import conn_manager
from src.pipeline.exceptions import ConnectionNotFoundError, DBConfigError
from src.pipeline.schemas import ConnectionConfig

router = APIRouter()


@router.post(
    "/connect/demo",
    summary="Connect to the demo dataset",
    description="Connect instantly to the built-in demo database. No credentials required.",
    response_model=dict[str, str],
)
def connect_demo() -> dict[str, str]:
    conn_manager.connect(connection_string=str(settings.DATABASE_URL))
    return {"status": "connected", "database": "demo"}


@router.post(
    "/connect/custom",
    summary="Connect to a custom database",
    description="Establish a database connection using the provided credentials.",
    response_model=dict[str, str],
)
def connect(config: Annotated[ConnectionConfig, Form()]) -> dict[str, str]:
    url = f"{config.dbms.scheme}://{config.username}:{config.password}@{config.host}:{config.port}/{config.db}"
    try:
        conn_manager.connect(connection_string=url)
    except DBConfigError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not connect to database. Check your credentials and try again.",
        )
    return {"status": "connected", "database": config.db}


@router.get(
    "/is-connected",
    summary="View connection status",
    description="Identify whether an active database connection is currently established.",
)
def is_connected() -> bool:
    return conn_manager.is_connected()


@router.post(
    "/disconnect",
    summary="Disconnect from the database",
    description="Terminate the active database connection associated with the provided token.",
)
def disconnect() -> str:
    try:
        # Terminate connection
        conn_manager.disconnect()
        return "Connection successfully terminated."
    except ConnectionNotFoundError:
        return "No active database connection found."
