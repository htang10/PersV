# ruff: noqa: ANN201
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter

from src.core.schemas import MessageResponse
from src.pipeline.config import pl_settings
from src.pipeline.database import conn_manager
from src.pipeline.exceptions import ConnectionNotFoundError, DBConfigError
from src.pipeline.schemas import ConnectionCheck, ConnectionConfig, SuccessConnection

router = APIRouter()


@router.post(
    "/connect/demo",
    summary="Connect to the demo dataset",
    description="Connect instantly to the built-in demo database. No credentials required.",
    response_model=SuccessConnection,
)
def connect_demo():
    conn_manager.connect(connection_string=str(pl_settings.DEMO_DB_URL), db_name="demo")
    return SuccessConnection


@router.post(
    "/connect/custom",
    summary="Connect to a custom database",
    description="Establish a database connection using the provided credentials.",
    response_model=SuccessConnection,
)
def connect(config: ConnectionConfig):
    url = f"{config.dbms.scheme}://{config.username}:{config.password}@{config.host}:{config.port}/{config.db}"
    try:
        conn_manager.connect(connection_string=url, db_name=config.db)
    except DBConfigError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not connect to database. Check your credentials and try again.",
        )
    return SuccessConnection(database=config.db)


@router.get(
    "/is-connected",
    summary="View connection status",
    description="Identify whether an active database connection is currently established.",
    response_model=ConnectionCheck,
)
def is_connected():
    return ConnectionCheck(
        connected=conn_manager.is_connected(), database=conn_manager.get_db_name()
    )


@router.post(
    "/disconnect",
    summary="Disconnect from the database",
    description="Terminate the active database connection associated with the provided token.",
    response_model=MessageResponse,
)
def disconnect():
    try:
        # Terminate connection
        conn_manager.disconnect()
        return JSONResponse({"message": "Connection successfully terminated."})
    except ConnectionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active database connection found.",
        )
