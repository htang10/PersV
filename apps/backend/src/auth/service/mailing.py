import logging
import smtplib
from contextlib import contextmanager
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import (
    SMTPAuthenticationError,
    SMTPConnectError,
    SMTPException,
    SMTPRecipientsRefused,
)
from typing import Any, Generator

from jinja2 import Environment, PackageLoader, TemplateSyntaxError, select_autoescape
from jinja2.exceptions import TemplateNotFound

from src.auth.config import auth_settings
from src.auth.service.otp import generate_code, save_code
from src.auth.utils import html_to_text

logger = logging.getLogger(__name__)


def _render_template(template_name: str, **kwargs: Any) -> tuple[str, str]:
    env = Environment(
        loader=PackageLoader("src.auth", "templates"), autoescape=select_autoescape()
    )
    html_content = env.get_template(template_name).render(**kwargs)
    text_content = html_to_text(html_content)
    return html_content, text_content


def _send_email(recipient: str, message: MIMEMultipart) -> None:
    with smtplib.SMTP(auth_settings.SMTP_HOST, auth_settings.SMTP_PORT) as server:
        server.starttls()
        server.login(auth_settings.SMTP_USERNAME, auth_settings.SMTP_PASSWORD)
        server.sendmail(auth_settings.FROM_EMAIL, recipient, message.as_string())


@contextmanager
def handle_mailing_errors() -> Generator[None, Any, None]:
    """A context manager that catches template errors, SMTP errors and database error."""
    try:
        yield
    except (TemplateNotFound, TemplateSyntaxError) as e:
        logger.error(f"Template error: {e}")
    except SMTPAuthenticationError as e:
        logger.error(f"SMTP authentication error: {e}")
    except SMTPConnectError as e:
        logger.error(f"SMTP connection error: {e}")
    except SMTPRecipientsRefused as e:
        logger.error(f"SMTP recipient refused error: {e}")
    except SMTPException as e:
        logger.error(f"Unexpected SMTP error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")


def send_login_otp(email: str) -> None:
    """Generates a login OTP code and emails it to the user.

    Args:
        email: The recipient's email address.
    """
    with handle_mailing_errors():
        expiry = auth_settings.OTP_EXP
        raw_code, hashed_code = generate_code()
        save_code(hashed_code, email, expiry)

        html_content, text_content = _render_template(
            "login.html",
            code=raw_code,
            expire_minutes=int(expiry.total_seconds() // 60),
        )

        message = MIMEMultipart("alternative")
        message["From"] = auth_settings.FROM_EMAIL
        message["To"] = email
        message["Subject"] = "Confirmation code to log in your account"
        message.attach(MIMEText(text_content, "plain"))
        message.attach(MIMEText(html_content, "html"))

        _send_email(email, message)
