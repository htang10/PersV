import random
import string
from hashlib import sha512

import html2text


def hash_secret(value: str) -> str:
    """Hashes a value using SHA-512 and returns the hex digest."""
    return sha512(value.encode("utf-8")).hexdigest()


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
