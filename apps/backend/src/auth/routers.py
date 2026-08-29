# ruff: noqa: ANN201
from fastapi import Cookie, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from fastapi.routing import APIRouter

from src.auth.dependencies import AuthSessionDep
from src.auth.exceptions import InvalidCode, UserNotFound
from src.auth.repository import create_user, get_user_by_email, update_login_metadata
from src.auth.schemas import AuthResponse, OTPLoginRequest, OTPRequest
from src.auth.service.otp import delete_code, verify_code
from src.auth.service.tokens import (
    create_access_token,
    create_refresh_token,
    delete_refresh_token_cookie,
    revoke_refresh_token,
    rotate_refresh_token,
    set_refresh_token_cookie,
)
from src.auth.tasks import send_login_otp_task
from src.auth.throttles import (
    login_1h_email,
    login_5m_email,
    login_10m_ip,
    otp_1h_email,
    otp_10m_email,
    otp_10m_ip,
)
from src.core.rate_limiter import check_limits, record_hits
from src.core.schemas import MessageResponse

router = APIRouter()


@router.post(
    "/generate-otp",
    summary="Request a one-time password",
    description="""Sends a time-limited one-time password to the provided email address.
    Use the returned code with `POST /auth/login` to authenticate.""",
    response_model=MessageResponse,
)
def generate_otp(body: OTPRequest, request: Request):
    email = body.email
    limits = [
        (otp_10m_email, "otp_request", "email", email),
        (otp_1h_email, "otp_request", "email", email),
        (otp_10m_ip, "otp_request", "ip", request.client.host),
    ]
    check_limits(limits)

    send_login_otp_task.delay(email)

    record_hits(limits)
    return MessageResponse(message=f"Confirmation code has been sent to {email}.")


@router.post(
    "/login",
    summary="Authenticate with a one-time password",
    description="""Verifies the one-time password sent to the provided email.
    Creates a new account if the email is unrecognized. 
    Returns a JWT access token and refresh token on success.""",
    response_model=AuthResponse,
)
def login(body: OTPLoginRequest, session: AuthSessionDep, request: Request):
    email = body.email
    code = body.code
    limits = [
        (login_5m_email, "login", "email", email),
        (login_1h_email, "login", "email", email),
        (login_10m_ip, "login", "ip", request.client.host),
    ]
    check_limits(limits)

    try:
        verify_code(email, code)
        delete_code(email)
    except InvalidCode:
        record_hits(limits)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email or passcode."
        )

    try:  # Login
        user = get_user_by_email(email, session)
    except UserNotFound:  # Sign-up
        user = create_user(email, session)

    # Update user metadata
    ip_address = request.headers.get("X-Forwarded-For", request.client.host)
    update_login_metadata(user, ip_address, session)

    user_id = str(user.id)
    response = JSONResponse({"token": create_access_token(user_id), "type": "Bearer"})
    set_refresh_token_cookie(response, refresh_token=create_refresh_token(user_id))
    return response


@router.post(
    "/logout",
    summary="Revoke the current session",
    description="""Invalidates the refresh token stored in the HTTP-only cookie, ending the current session.
    The client is responsible for discarding the access token.""",
    status_code=status.HTTP_204_NO_CONTENT,
)
def logout(response: Response, refresh_token: str = Cookie(include_in_schema=False)):
    revoke_refresh_token(refresh_token)
    delete_refresh_token_cookie(response)
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.post(
    "/refresh",
    summary="Rotate refresh token and issue new access token",
    description="""Validates the refresh token stored in the HTTP-only cookie,
    issues a new access token, and rotates the refresh token.
    The rotated refresh token is set as an HTTP-only cookie.""",
    response_model=AuthResponse,
)
def refresh_tokens(refresh_token: str = Cookie(include_in_schema=False)):
    new_access_token, new_refresh_token = rotate_refresh_token(refresh_token)
    response = JSONResponse({"token": new_access_token, "type": "Bearer"})
    set_refresh_token_cookie(response, refresh_token=new_refresh_token)
    return response
