import logging

from fastapi import HTTPException, status
from fastapi.routing import APIRouter

from src.connection.config import conn_settings
from src.connection.database import custom_conn_manager
from src.connection.dependencies.anon_id import UserId
from src.connection.dependencies.sqlite import SQLiteDBFile
from src.connection.exceptions import (
    ConnectionNotFoundError,
    DBConfigError,
)
from src.connection.schemas import (
    ClientServerConnectionConfig,
    ConnectionStatus,
    EmbeddedConnectionConfig,
)
from src.core.responses import APIResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/demo",
    summary="Connect to the demo dataset",
    description="Connect instantly to the built-in demo database. No credentials required.",
    response_model=ConnectionStatus,
)
def connect_demo(user_id: UserId):
    try:
        custom_conn_manager.connect(
            user_id=user_id, schema=conn_settings.PG_DEMO_SCHEMA
        )
        return ConnectionStatus(connected=True, database="demo")
    except DBConfigError:
        raise HTTPException(
            detail="The demo database is temporarily unavailable. Please try again later.",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


@router.post(
    "/custom",
    summary="Connect to a custom database",
    description="Establish a database connection using the provided credentials.",
    response_model=ConnectionStatus,
)
def connect(config: ClientServerConnectionConfig, user_id: UserId):
    try:
        custom_conn_manager.connect(
            user_id=user_id,
            schema=config.db_schema,
            url=config.to_url(),
        )
        return ConnectionStatus(connected=True, database=config.db)
    except DBConfigError:
        raise HTTPException(
            detail="Could not connect to database. Check your credentials and try again.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@router.post(
    "/custom/sqlite",
    summary="Connect to a SQLite database",
    description="Establish a SQLite database connection.",
    response_model=ConnectionStatus,
)
def connect_sqlite(db_file: SQLiteDBFile, user_id: UserId):
    config = EmbeddedConnectionConfig(db_path=db_file.file_path)
    try:
        custom_conn_manager.connect(
            user_id=user_id,
            url=config.to_url(),
        )
        return ConnectionStatus(connected=True, database=db_file.file_name)
    except DBConfigError:
        raise HTTPException(
            detail="Unable to connect to the SQLite database. Ensure the uploaded file is valid and accessible.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@router.get(
    "/status",
    summary="View connection status",
    description="Identify whether an active database connection is currently established.",
    response_model=ConnectionStatus,
)
def is_connected(user_id: UserId):
    return custom_conn_manager.get_connection_status(user_id=user_id)


@router.delete(
    "",
    summary="Disconnect from the database",
    description="Terminate the active database connection and clear the associated session state.",
)
def disconnect(response: APIResponse, user_id: UserId):
    try:
        # Terminate connection
        custom_conn_manager.disconnect(user_id=user_id)
        custom_conn_manager.clear_user_lock(user_id=user_id)
        response.status_code = status.HTTP_204_NO_CONTENT
        return response
    except ConnectionNotFoundError:
        logger.warning("User did not establish a database connection before querying.")
        raise HTTPException(
            detail="No active database connection found.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
