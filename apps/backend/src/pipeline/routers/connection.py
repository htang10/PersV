# ruff: noqa: ANN201
import logging

from fastapi import HTTPException, status
from fastapi.routing import APIRouter

from src.auth.dependencies import AuthUserId, CurrentUserId, OptionalUserId
from src.auth.service.identities import delete_anon_id_cookie
from src.core.responses import APIResponse
from src.pipeline.config import pl_settings
from src.pipeline.database import custom_conn_manager
from src.pipeline.exceptions import (
    ConnectionNotFoundError,
    DBConfigError,
)
from src.pipeline.schemas import ConnectionConfig, ConnectionStatus

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/connect/demo",
    summary="Connect to the demo dataset",
    description="Connect instantly to the built-in demo database. No credentials required.",
    response_model=ConnectionStatus,
)
def connect_demo(user_id: CurrentUserId):
    try:
        custom_conn_manager.connect(user_id=user_id, schema=pl_settings.PG_DEMO_SCHEMA)
        return ConnectionStatus(connected=True, database="demo")
    except DBConfigError:
        raise HTTPException(
            detail="The demo database is temporarily unavailable. Please try again later.",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


@router.post(
    "/connect/custom",
    summary="Connect to a custom database",
    description="Establish a database connection using the provided credentials.",
    response_model=ConnectionStatus,
)
def connect(config: ConnectionConfig, user_id: AuthUserId):
    url = f"{config.dbms.scheme}://{config.username}:{config.password}@{config.host}:{config.port}/{config.db}"
    try:
        custom_conn_manager.connect(
            user_id=user_id,
            schema=config.db_schema,
            url=url,
        )
        return ConnectionStatus(connected=True, database=config.db)
    except DBConfigError:
        raise HTTPException(
            detail="Could not connect to database. Check your credentials and try again.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@router.get(
    "/is-connected",
    summary="View connection status",
    description="Identify whether an active database connection is currently established.",
    response_model=ConnectionStatus,
)
def is_connected(user_id: OptionalUserId):
    return custom_conn_manager.get_connection_status(user_id=user_id)


@router.post(
    "/disconnect",
    summary="Disconnect from the database",
    description="Terminate the active database connection and clear the associated session state.",
)
def disconnect(response: APIResponse, user_id: OptionalUserId):
    try:
        # Terminate connection
        custom_conn_manager.disconnect(user_id=user_id)
        custom_conn_manager.clear_user_lock(user_id=user_id)
        response.status_code = status.HTTP_204_NO_CONTENT
        delete_anon_id_cookie(response)
        return response
    except ConnectionNotFoundError:
        logger.warning("User did not establish a database connection before querying.")
        raise HTTPException(
            detail="No active database connection found.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )
