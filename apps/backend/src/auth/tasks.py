from src.auth.service.mailing import send_login_otp
from src.core.celery_app import app


@app.task
def send_login_otp_task(email: str) -> None:
    """Celery task wrapper for sending a login OTP email asynchronously.

    Args:
        email: The recipient's email address.
    """
    send_login_otp(email)
