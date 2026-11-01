from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.auth.exceptions import EmailAlreadyUsed, EmailUnchanged
from src.auth.models import User
from src.auth.repository import update_login_metadata
from src.auth.service.otp import delete_code, verify_code


def change_email(
    user: User,
    new_email: str,
    new_email_code: str,
    current_email_code: str,
    ip_address: str,
    db_session: Session,
) -> None:
    """Changes a user's email address after verifying both inboxes.

    Raises:
        EmailUnchanged: new_email is already the user's email.
        InvalidEmailOrOTP: Either code is incorrect or expired.
        EmailAlreadyUsed: new_email belongs to another user.
    """
    if user.email == new_email:
        raise EmailUnchanged

    verify_code(email=new_email, code=new_email_code)
    verify_code(email=user.email, code=current_email_code)
    delete_code(email=new_email)
    delete_code(email=user.email)

    user.email = new_email
    try:
        update_login_metadata(user=user, ip_address=ip_address, db_session=db_session)
    except IntegrityError:
        db_session.rollback()
        raise EmailAlreadyUsed
