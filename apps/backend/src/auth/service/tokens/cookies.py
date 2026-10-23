"""Refresh token cookie: attributes and helpers for setting and clearing it.

The cookie is HTTP-only, Secure and SameSite=Strict, and its lifetime follows
`REFRESH_TOKEN_EXP`. These helpers keep every attribute in one place, so the
cookie is always set and cleared with matching settings.
"""

from fastapi import Response

from src.auth.config import auth_settings

REFRESH_TOKEN_EXP_SECONDS = int(auth_settings.REFRESH_TOKEN_EXP.total_seconds())
COOKIE_NAME = "refresh_token"


def set_refresh_token_cookie(response: Response, refresh_token: str) -> None:
    """Sets the refresh token cookie on a response.

    Cookie attributes:
       max_age: `REFRESH_TOKEN_EXP_SECONDS`, so the browser discards the
           cookie when the token's own lifetime ends.
       secure: Only sent over HTTPS. Most browsers treat localhost as a
           secure context, so this usually works in local development.
       httponly: Not readable from JavaScript, which limits token theft via
           XSS.
       samesite="strict": Never sent on cross-site requests, including
           navigation arriving from another site. The first request after
           following an external link therefore carries no cookie.

    Args:
       response: The response to attach the cookie to.
       refresh_token: The raw refresh token to store.
    """
    response.set_cookie(
        key=COOKIE_NAME,
        value=refresh_token,
        max_age=REFRESH_TOKEN_EXP_SECONDS,
        secure=True,
        httponly=True,
        samesite="strict",
    )


def delete_refresh_token_cookie(response: Response) -> None:
    """Instructs the browser to delete the refresh token cookie.

    Uses the same attributes as the cookie it replaces, so the browser
    recognizes and removes it.

    Args:
        response: The response to attach the deletion to.
    """
    response.delete_cookie(
        key=COOKIE_NAME,
        secure=True,
        httponly=True,
        samesite="strict",
    )
