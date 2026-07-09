from typing import Annotated, Any, Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from src.auth.exceptions import UserNotFound
from src.auth.models import User
from src.auth.repository import get_user_by_id
from src.auth.service.tokens import validate_access
from src.config import settings

auth_engine = create_engine(str(settings.DATABASE_URL))
security = HTTPBearer()


def get_auth_db() -> Generator[Session, Any, None]:
    with Session(auth_engine) as session:
        yield session


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
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


AuthSessionDep = Annotated[Session, Depends(get_auth_db)]
CurrentUser = Annotated[User, Depends(get_current_active_user)]
