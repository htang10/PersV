import logging
from typing import Annotated, Any, Generator

from fastapi import Cookie, Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.auth.config import auth_settings
from src.auth.exceptions import InvalidAccessToken, InvalidRefreshToken
from src.auth.rate_limits import anon_id_rl
from src.auth.repository import get_user_by_id
from src.auth.service.identities import (
    generate_anon_id,
    is_valid_anon_id,
    set_anon_id_cookie,
)
from src.auth.service.tokens import (
    rotate_refresh_token,
    set_refresh_token_cookie,
    validate_access,
)
from src.core.utils import get_sqlalchemy_url

__all__ = [
    "AuthSessionDep",  # Login
    "AuthUserId",  # Custom connect, Profile
    "OptionalUserId",  # Connection check, Disconnect, Querying
    "CurrentUserId",  # Demo connect
]

AUTH_ENGINE = create_engine(
    get_sqlalchemy_url(
        username=auth_settings.PG_AUTH_USER, password=auth_settings.PG_AUTH_PASSWORD
    ),
    pool_pre_ping=True,
    pool_recycle=300,
)
required_bearer = HTTPBearer()
optional_bearer = HTTPBearer(auto_error=False)
logger = logging.getLogger(__name__)


def get_auth_db() -> Generator[Session, Any, None]:
    """Provides a transactional database session for the authentication database.

    Session is automatically closed after the request lifecycle completes.

    Yields:
        A SQLAlchemy session connected to the authentication database.
    """
    with Session(AUTH_ENGINE) as db_session:
        yield db_session


def _authenticate(
    response: Response,
    access_token: str | None,
    refresh_token: str,
    db_session: Session,
) -> str:
    """Validates access token and, if needed, refresh token.

    If access token is either missing or invalid, a full token rotation is performed.

    Returns:
        The user id.

    Raises:
        401: If both tokens are missing or invalid.
        403: If the user account is inactive.
    """
    user_id = None
    rotation = None
    if access_token:
        try:
            # Check if the primary access token is present and valid
            user_id = str(validate_access(access_token)["sub"])
        except InvalidAccessToken:
            pass

    if user_id is None:
        try:
            # Access token expired; attempt token rotation using the refresh token
            rotation = rotate_refresh_token(token=refresh_token)
        except InvalidRefreshToken:
            logger.warning(
                "User session has expired due to an invalid or missing refresh token."
            )
            raise HTTPException(
                detail="Invalid or expired authentication tokens.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        # Validate the newly generated access token and get the user ID
        user_id = rotation.user_id

    if not get_user_by_id(user_id=user_id, db_session=db_session).is_active:
        raise HTTPException(
            detail="Inactive user.", status_code=status.HTTP_403_FORBIDDEN
        )

    # Persist the new tokens in the response headers and cookies
    if rotation:
        new_access_token = rotation.access_token
        new_refresh_token = rotation.refresh_token
        if new_access_token and new_refresh_token:
            set_refresh_token_cookie(response, refresh_token=new_refresh_token)
            response.headers["X-New-Access-Token"] = new_access_token

    return user_id


def get_auth_user_id(
    response: Response,
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(required_bearer)],
    refresh_token: str | None = Cookie(default=None, include_in_schema=False),
    db_session: Session = Depends(get_auth_db),
) -> str:
    """Authenticates the user and requires a valid session.

    Returns:
        The user id.

    Raises:
        401: If credentials were missing or invalid.
        403: If the user account is inactive.
    """
    if not refresh_token:
        logger.warning(
            "User session has expired due to an invalid or missing refresh token."
        )
        raise HTTPException(
            detail="Invalid or expired authentication tokens.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    access_token = credentials.credentials if credentials else None
    return _authenticate(response, access_token, refresh_token, db_session)


def get_optional_auth_user_id(
    response: Response,
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(optional_bearer)
    ],
    refresh_token: str | None = Cookie(default=None, include_in_schema=False),
    session: Session = Depends(get_auth_db),
) -> str | None:
    """Authenticates the user if signed in, otherwise treats them as a guest.

    Returns:
        The user id, or None if the user is a guest.

    Raises:
        401: If credentials were missing or invalid.
        403: If the user account is inactive.
    """
    if not refresh_token:
        return None  # Guest, regardless of any access token
    access_token = credentials.credentials if credentials else None
    return _authenticate(response, access_token, refresh_token, session)


def get_optional_current_user_id(
    response: Response,
    user_id: str | None = Depends(get_optional_auth_user_id),
    anon_id: str | None = Cookie(default=None, include_in_schema=False),
) -> str | None:
    """Identifies whether the current user is a guest/anonymous user or an authenticated user.

    Returns:
        The user id. None if not found/recognized.
    """
    if anon_id and is_valid_anon_id(anon_id):
        # Reset the expiration whenever an existing anonymous id is reused
        set_anon_id_cookie(response=response, anon_id=anon_id)
        return anon_id

    return user_id


def get_current_user_id(
    response: Response,
    request: Request,
    user_id: str | None = Depends(get_optional_auth_user_id),
    anon_id: str | None = Cookie(default=None, include_in_schema=False),
) -> str:
    """Identifies whether the current user is a guest/anonymous user or an authenticated user.

    If not yet recognized/registered, generates a new anonymous ID for the current user.

    Returns:
        The user id, or a newly generated anonymous ID.
    """
    current_user_id = get_optional_current_user_id(
        response=response,
        user_id=user_id,
        anon_id=anon_id,
    )

    if current_user_id:
        return current_user_id

    anon_id_rl.consume(ip=request.client.host)

    new_anon_id = generate_anon_id()
    set_anon_id_cookie(response, anon_id=new_anon_id)
    return new_anon_id


AuthSessionDep = Annotated[Session, Depends(get_auth_db)]
AuthUserId = Annotated[str, Depends(get_auth_user_id)]
OptionalUserId = Annotated[str | None, Depends(get_optional_current_user_id)]
CurrentUserId = Annotated[str, Depends(get_current_user_id)]
