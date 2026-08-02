# ruff: noqa: ANN201
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter

from src.auth.dependencies import CurrentUser
from src.core.schemas import MessageResponse
from src.pipeline.database import custom_conn_manager
from src.pipeline.exceptions import ConnectionNotFoundError, DBConfigError
from src.pipeline.schemas import ConnectionConfig, ConnectionStatus, SuccessConnection

router = APIRouter()


@router.post(
    "/connect/demo",
    summary="Connect to the demo dataset",
    description="Connect instantly to the built-in demo database. No credentials required.",
    response_model=SuccessConnection,
)
def connect_demo(current_user: CurrentUser):
    user_id = str(current_user.id)
    custom_conn_manager.connect(user_id=user_id)
    return SuccessConnection(database="demo")


@router.post(
    "/connect/custom",
    summary="Connect to a custom database",
    description="Establish a database connection using the provided credentials.",
    response_model=SuccessConnection,
)
def connect(config: ConnectionConfig, current_user: CurrentUser):
    user_id = str(current_user.id)
    url = f"{config.dbms.scheme}://{config.username}:{config.password}@{config.host}:{config.port}/{config.db}"
    try:
        custom_conn_manager.connect(
            user_id=user_id,
            url=url,
            schema=config.db_schema,
        )
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
    response_model=ConnectionStatus,
)
def is_connected(current_user: CurrentUser):
    user_id = str(current_user.id)
    return custom_conn_manager.get_connection_status(user_id=user_id)


@router.post(
    "/disconnect",
    summary="Disconnect from the database",
    description="Terminate the active database connection associated with the provided token.",
    response_model=MessageResponse,
)
def disconnect(current_user: CurrentUser):
    user_id = str(current_user.id)
    try:
        # Terminate connection
        custom_conn_manager.disconnect(user_id=user_id)
        custom_conn_manager.clear_user_lock(user_id=user_id)
        return JSONResponse({"message": "Connection successfully terminated."})
    except ConnectionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active database connection found.",
        )
