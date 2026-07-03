import logging
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from src.auth.exceptions import UserNotFound
from src.auth.models import User
from src.auth.utils import display_name_from_email

logger = logging.getLogger(__name__)


def get_user_by_email(email: str, session: Session) -> User:
    try:
        return session.execute(select(User).filter_by(email=email)).scalar_one()
    except NoResultFound as e:
        logger.error(e)
        raise UserNotFound


def create_user(email: str, session: Session) -> User:
    user = User(email=email, display_name=display_name_from_email(email))
    session.add(user)
    session.commit()
    return user


def update_login_metadata(user: User, ip_address: str, session: Session) -> None:
    session.execute(
        update(User)
        .where(User.email == user.email)
        .values(last_login_at=datetime.now(timezone.utc), last_login_ip=ip_address)
    )
    session.commit()
