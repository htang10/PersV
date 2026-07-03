from src.auth.service.mailing import send_login_otp
from src.celery import app


@app.task
def send_login_otp_task(email: str) -> None:
    send_login_otp(email)
