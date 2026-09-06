from typing import Annotated, Any, Generator

from fastapi import Cookie, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.auth.config import auth_settings
from src.auth.exceptions import UserNotFound
from src.auth.repository import get_user_by_id
from src.auth.service.identities import (
    generate_anon_id,
    is_valid_anon_id,
    set_anon_id_cookie,
)
from src.auth.service.tokens import validate_access
from src.auth.throttles import anon_1h_ip, anon_15m_ip
from src.core.rate_limiter import check_limits, record_hits

AUTH_ENGINE = create_engine(str(auth_settings.AUTH_DB_URL))
required_bearer = HTTPBearer()
optional_bearer = HTTPBearer(auto_error=False)


def get_auth_db() -> Generator[Session, Any, None]:
    """Dependency that yields a database session for authentication."""
    with Session(AUTH_ENGINE) as session:
        yield session


def get_auth_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(required_bearer)],
) -> str:
    """Authenticates a user given their credentials.

    Returns:
        The user's ID.

    Raises:
        401: if no token is provided, or it fails validation.
    """
    try:
        payload = validate_access(credentials)
        return str(payload["sub"])
    except UserNotFound:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )


def get_active_auth_user_id(
    auth_user_id: str = Depends(get_auth_user_id),
    session: Session = Depends(get_auth_db),
) -> str:
    """Authenticates a user given their credentials, but also require the user's
    account to be active.

    Returns:
        The user's ID.

    Raises:
        403: if the user is not active.
    """
    auth_user = get_user_by_id(auth_user_id, session)
    if not auth_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )
    return auth_user_id


def get_optional_auth_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(optional_bearer)],
) -> str | None:
    """Authenticates a user given their credentials.

    Returns:
        The user's ID.

    Returns:
        None if no token is provided or validation fails.
    """
    payload = validate_access(credentials)
    if not payload:
        return None
    return str(payload["sub"])


def get_optional_current_user_id(
    user_id: str | None = Depends(get_optional_auth_user_id),
    anon_id: str | None = Cookie(default=None, include_in_schema=False),
) -> str | None:
    """Detects whether the current user is a guest/anonymous or an authenticated user.

    Returns:
        The user's id.
        None if the user is not found/recognized.
    """
    if user_id:
        with Session(AUTH_ENGINE) as session:
            return get_active_auth_user_id(
                auth_user_id=user_id,
                session=session,
            )

    if anon_id and is_valid_anon_id(anon_id):
        return anon_id

    return None


def get_current_user_id(
    response: Response,
    request: Request,
    user_id: str | None = Depends(get_optional_auth_user_id),
    anon_id: str | None = Cookie(default=None, include_in_schema=False),
) -> str:
    """Detects whether the current user is a guest/anonymous or an authenticated user.

    If not yet recognized, generates a new anonymous ID for the current user.

    Returns:
        The user's id, or a newly generated anonymous ID.
    """
    current_user_id = get_optional_current_user_id(
        user_id=user_id,
        anon_id=anon_id,
    )

    if current_user_id:
        return current_user_id

    anon_conn_limit = [
        (anon_15m_ip, "anon_conn", "ip", request.client.host),
        (anon_1h_ip, "anon_conn", "ip", request.client.host),
    ]
    check_limits(anon_conn_limit)
    record_hits(anon_conn_limit)

    new_anon_id = generate_anon_id()
    set_anon_id_cookie(response, anon_id=new_anon_id)
    return new_anon_id


AuthSessionDep = Annotated[Session, Depends(get_auth_db)]  # Login
AuthUserId = Annotated[str, Depends(get_active_auth_user_id)]  # Custom connect
OptionalUserId = Annotated[
    str | None, Depends(get_optional_current_user_id)
]  # Connection check, Disconnect, Querying
CurrentUserId = Annotated[str, Depends(get_current_user_id)]  # Demo connect
