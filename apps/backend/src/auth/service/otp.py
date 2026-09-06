import hashlib
import hmac
import secrets
from datetime import timedelta

from src.auth.config import auth_settings
from src.auth.exceptions import InvalidCode
from src.core.redis_client import redis_client


def hash_secret(otp: str, secret: bytes) -> str:
    """Hashes an OTP with a server-side secret key (HMAC), so stored hashes can't be brute-forced
    offline even if the Redis store is compromised."""
    return hmac.new(secret, otp.encode(), hashlib.sha256).hexdigest()


def generate_code(length: int = 6) -> tuple[str, str]:
    """Generates a numeric OTP and returns it as a (plain, hashed) tuple."""
    code = "".join([str(secrets.randbelow(10)) for _ in range(length)])
    secret_bytes = bytes.fromhex(auth_settings.OTP_SECRET_KEY)
    hashed_code = hash_secret(code, secret_bytes)
    return code, hashed_code


def save_code(hashed_code: str, email: str, expiry: timedelta) -> None:
    """Stores the hashed OTP in Redis keyed by email with the given expiry."""
    redis_client.setex(f"otp:{email}", expiry, hashed_code)


def verify_code(email: str, code: str) -> None:
    """Validates the OTP against the stored hash using a timing-safe comparison.

    Raises:
        InvalidCode: The OTP is missing or incorrect.
    """
    secret_bytes = bytes.fromhex(auth_settings.OTP_SECRET_KEY)
    hashed_input = hash_secret(code, secret_bytes)
    stored = redis_client.get(f"otp:{email}")

    if stored is None or not hmac.compare_digest(hashed_input, stored):
        raise InvalidCode


def delete_code(email: str) -> None:
    redis_client.delete(f"otp:{email}")
