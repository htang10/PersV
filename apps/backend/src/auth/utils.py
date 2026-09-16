import hashlib
import hmac
import random
import string

import html2text

from src.auth.config import auth_settings


def html_to_text(html_content: str) -> str:
    """Generates a plain text from HTML content."""
    converter = html2text.HTML2Text()
    converter.ignore_links = False
    converter.ignore_images = False
    converter.body_width = 0
    return converter.handle(html_content)


def display_name_from_email(email: str) -> str:
    """Generates a display name from an email address."""
    return (
        email.split("@")[0]
        if len(email.split("@"))
        else "".join(random.choice(string.ascii_letters) for _ in range(6))
    )


def hash_credential(credential: str) -> str:
    """Hashes a credential with a server-side secret key (HMAC), so stored hashes can't be brute-forced
    offline even if the Redis store is compromised."""
    return hmac.new(
        bytes.fromhex(auth_settings.CREDENTIAL_HMAC_SECRET_KEY),
        credential.encode(),
        hashlib.sha256,
    ).hexdigest()
