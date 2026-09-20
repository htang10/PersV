# ruff: noqa: ANN201
import logging

from fastapi import Cookie, HTTPException, Request, status
from fastapi.routing import APIRouter

from src.auth.config import auth_settings
from src.auth.dependencies import AuthSessionDep, AuthUserId
from src.auth.exceptions import InvalidAuthToken, InvalidEmailOrOTP, UserNotFound
from src.auth.repository import create_user, get_user_by_email, update_login_metadata
from src.auth.schemas import AuthResponse, OTPLoginRequest, OTPRequest, OTPResponse
from src.auth.service.otp import delete_code, verify_code
from src.auth.service.tokens import (
    create_access_token,
    create_refresh_token,
    delete_refresh_token_cookie,
    revoke_all_user_sessions,
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
from src.core.responses import APIResponse

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/otp",
    summary="Request a one-time password",
    description="""Sends a time-limited one-time password to the provided email address.
    Use the returned code with `POST /auth/login` to authenticate.""",
    response_model=OTPResponse,
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

    expiry = auth_settings.OTP_EXP.total_seconds()
    return OTPResponse(to=email, expires_in=expiry)


@router.post(
    "/login",
    summary="Authenticate with a one-time password",
    description="""Verifies the code sent to the provided email.
    Creates a new account if the email is unrecognized. 
    Generates authentication tokens on success.""",
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
    except InvalidEmailOrOTP:
        record_hits(limits)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or passcode.",
        )

    try:  # Login
        logger.info(f"Existing user found with email {email}. Attempt login.")
        user = get_user_by_email(email, session)
    except UserNotFound:  # Sign-up
        logger.info(f"No user found with email {email}. Attempt sign-up.")
        user = create_user(email, session)

    # Update user metadata
    ip_address = request.headers.get("X-Forwarded-For", request.client.host)
    update_login_metadata(user=user, ip_address=ip_address, session=session)

    user_id = str(user.id)
    response = APIResponse(
        content=AuthResponse(
            token=create_access_token(user_id=user_id),
        ).model_dump()
    )
    set_refresh_token_cookie(
        response, refresh_token=create_refresh_token(user_id=user_id)
    )
    return response


@router.post(
    "/logout",
    summary="Revoke the current session",
    description="""Invalidates the refresh token stored in the HTTP-only cookie,
    ending the current session. The client is responsible for discarding the access token.""",
)
def logout(response: APIResponse, refresh_token: str = Cookie(include_in_schema=False)):
    revoke_refresh_token(refresh_token)
    delete_refresh_token_cookie(response)
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.post(
    "/logout-all",
    summary="Revoke all sessions",
    description="""Invalidates all refresh tokens belonging to the user,
    ending all sessions including the current one. The client is responsible
    for discarding the access token.""",
)
def logout_all_sessions(response: APIResponse, user_id: AuthUserId):
    revoke_all_user_sessions(user_id=user_id)
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
    try:
        new_access_token, new_refresh_token = rotate_refresh_token(refresh_token)
    except InvalidAuthToken:
        logger.warning("User's refresh token has expired or is invalid.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated.",
        )

    response = APIResponse(
        content=AuthResponse(
            token=new_access_token,
        ).model_dump()
    )
    set_refresh_token_cookie(response, refresh_token=new_refresh_token)
    return response
