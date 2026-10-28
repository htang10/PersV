import logging

from sqlalchemy import update
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import Session

from src.auth.exceptions import UserNotFound
from src.auth.models import User
from src.profile.exceptions import EmailAlreadyUsed
from src.profile.schemas import UserProfileUpdate

logger = logging.getLogger(__name__)


def update_user(
    user_id: str, updated_info: UserProfileUpdate, db_session: Session
) -> None | User:
    """Updates user's profile with the provided information.

    Fields with null values (None) will not be updated.

    Returns:
        The user object with updated values

    Raises:
        UserNotFound: User with given id was not found.
        EmailAlreadyUsed: A different user already registered with the provided email address.
    """
    changes = updated_info.model_dump(exclude_none=True)
    # If no changes were made, skip updating
    if not changes:
        return None

    try:
        updated_user = db_session.execute(
            update(User).where(User.id == user_id).values(**changes).returning(User)
        ).scalar_one()
        if not updated_user:
            raise UserNotFound
        db_session.commit()
        return updated_user
    except NoResultFound as e:
        logger.warning(e)
        raise UserNotFound
    except IntegrityError as e:
        logger.warning(e)
        raise EmailAlreadyUsed
