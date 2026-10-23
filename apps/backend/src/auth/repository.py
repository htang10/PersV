import logging

from sqlalchemy import select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from src.auth.exceptions import UserNotFound
from src.auth.models import User
from src.auth.utils import display_name_from_email
from src.core.utils import get_current_datetime

logger = logging.getLogger(__name__)


def get_user_by_id(user_id: str, db_session: Session) -> User:
    """Retrieves a user by ID.

    Returns
        The user object associated with the given ID.

    Raises:
        UserNotFound: If no user exists with the given ID.
    """
    try:
        return db_session.execute(select(User).filter_by(id=user_id)).scalar_one()
    except NoResultFound as e:
        logger.warning(e)
        raise UserNotFound


def get_user_by_email(email: str, db_session: Session) -> User:
    """Retrieves a user by email address.

    Returns
        The user object associated with the given email address.

    Raises:
        UserNotFound: If no user exists with the given email address.
    """
    try:
        return db_session.execute(select(User).filter_by(email=email)).scalar_one()
    except NoResultFound as e:
        logger.warning(e)
        raise UserNotFound


def create_user(email: str, db_session: Session) -> User:
    """Creates a new user with the given email address.

    Returns
        The new user object associated with the given email address.
    """
    user = User(email=email, display_name=display_name_from_email(email))
    db_session.add(user)
    db_session.commit()
    return user


def update_login_metadata(user: User, ip_address: str, db_session: Session) -> None:
    """Updates user login metadata such as last login time and IP address."""
    db_session.execute(
        update(User)
        .where(User.email == user.email)
        .values(
            last_login_at=get_current_datetime().isoformat(), last_login_ip=ip_address
        )
    )
    db_session.commit()
