import hmac
import secrets
from datetime import timedelta

from src.auth.exceptions import InvalidCode
from src.auth.utils import hash_secret
from src.redis import redis_client


def generate_code(length: int = 6) -> tuple[str, str]:
    """Generates a numeric OTP and returns it as a (plain, hashed) tuple."""
    code = "".join([str(secrets.randbelow(10)) for _ in range(length)])
    hashed_code = hash_secret(code)
    return code, hashed_code


def save_code(hashed_code: str, email: str, minutes: int) -> None:
    """Stores the hashed OTP in Redis keyed by email with the given expiry."""
    redis_client.setex(f"otp:{email}", timedelta(minutes=minutes), hashed_code)


def verify_code(email: str, code: str) -> None:
    """Validates the OTP against the stored hash using a timing-safe comparison.

    Raises:
        InvalidCode: The OTP is missing or incorrect.
    """
    hashed_input = hash_secret(code)
    stored = redis_client.get(f"otp:{email}")

    if stored is None or not hmac.compare_digest(hashed_input, stored):
        raise InvalidCode


def delete_code(email: str) -> None:
    redis_client.delete(f"otp:{email}")
