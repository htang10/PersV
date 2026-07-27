from typing import Annotated, Any, Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.auth.config import auth_settings
from src.auth.exceptions import UserNotFound
from src.auth.models import User
from src.auth.repository import get_user_by_id
from src.auth.service.tokens import validate_access

AUTH_ENGINE = create_engine(str(auth_settings.AUTH_DB_URL))
required_bearer = HTTPBearer()
optional_bearer = HTTPBearer(auto_error=False)


def get_auth_db() -> Generator[Session, Any, None]:
    with Session(AUTH_ENGINE) as session:
        yield session


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(required_bearer)],
    session: Session = Depends(get_auth_db),
) -> User:
    try:
        payload = validate_access(credentials)
        return get_user_by_id(payload["sub"], session)
    except UserNotFound:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user"
        )
    return current_user


def get_optional_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(optional_bearer)],
    session: Session = Depends(get_auth_db),
) -> User | None:
    payload = validate_access(credentials)
    if not payload:
        return None
    return get_user_by_id(payload["sub"], session)


AuthSessionDep = Annotated[Session, Depends(get_auth_db)]
CurrentUser = Annotated[User, Depends(get_current_active_user)]
OptionalUser = Annotated[User | None, Depends(get_optional_user)]
