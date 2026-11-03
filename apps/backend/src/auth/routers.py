import logging

from fastapi import Cookie, HTTPException, Request, status
from fastapi.routing import APIRouter

from src.auth.config import auth_settings
from src.auth.dependencies import AuthSessionDep, AuthUserId
from src.auth.exceptions import (
    EmailAlreadyUsed,
    EmailUnchanged,
    InvalidEmailOrOTP,
    UserNotFound,
)
from src.auth.rate_limits import (
    email_change_success_rl,
    email_change_verification_rl,
    login_rl,
    otp_rl,
)
from src.auth.repository import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    update_login_metadata,
)
from src.auth.schemas import (
    AuthResponse,
    EmailChangeRequest,
    OTPLoginRequest,
    OTPRequest,
    OTPResponse,
    SessionValidationResponse,
)
from src.auth.service.email_change import change_email
from src.auth.service.otp import delete_code, verify_code
from src.auth.service.tokens import (
    create_access_token,
    create_refresh_token,
    delete_refresh_token_cookie,
    revoke_all_user_sessions,
    revoke_refresh_token,
    set_refresh_token_cookie,
    validate_refresh_token,
)
from src.auth.tasks import send_login_otp_task
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

    # Reject if the email or IP limit is exhausted. Counted once the code is queued.
    attempt = otp_rl.check(email=email, ip=request.client.host)
    # Sent in the background so the response does not wait on email delivery.
    send_login_otp_task.delay(email=email)
    attempt.record()

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

    # Reject if either limit is exhausted. Counted later, only on failed login.
    attempt = login_rl.check(email=email, ip=request.client.host)

    try:
        verify_code(email, code)
        delete_code(email)  # Single use: the code cannot be replayed.
    except InvalidEmailOrOTP:
        attempt.record()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or passcode.",
        )

    try:  # Login
        user = get_user_by_email(email, session)
        logger.info(f"Existing user found with email {email}. Attempt login.")
    except UserNotFound:  # Sign-up
        logger.info(f"No user found with email {email}. Attempt sign-up.")
        user = create_user(email, session)

    # Update user metadata. The forwarded header carries the client IP behind a proxy.
    ip_address = request.headers.get("X-Forwarded-For", request.client.host)
    update_login_metadata(user=user, ip_address=ip_address, db_session=session)

    # The access token goes in the body. The refresh token goes in a cookie and starts the session.
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


@router.get(
    "/session",
    summary="Validate the current session",
    description="""Validates the refresh token stored in the HTTP-only cookie.
    If invalid or not present, user loses access to protected endpoints.""",
    response_model=SessionValidationResponse,
)
def validate_session(
    refresh_token: str | None = Cookie(default=None, include_in_schema=False),
):
    # No cookie means no session.
    if refresh_token is None:
        return SessionValidationResponse(valid=False)
    return SessionValidationResponse(valid=validate_refresh_token(token=refresh_token))


@router.post(
    "/logout",
    summary="Revoke the current session",
    description="""Invalidates the refresh token stored in the HTTP-only cookie,
    ending the current session. The client is responsible for discarding the access token.""",
    status_code=status.HTTP_204_NO_CONTENT,
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
    status_code=status.HTTP_204_NO_CONTENT,
)
def logout_all_sessions(response: APIResponse, user_id: AuthUserId):
    revoke_all_user_sessions(user_id=user_id)
    delete_refresh_token_cookie(response)
    response.status_code = status.HTTP_204_NO_CONTENT
    return response


@router.put(
    "/email",
    summary="Update the email address",
    description="""Changes the account email after verifying a code sent to both
    the current and the new address. Generates new authentication tokens on success.""",
    response_model=AuthResponse
)
def change_email_address(
    user_id: AuthUserId,
    body: EmailChangeRequest,
    session: AuthSessionDep,
    request: Request,
):
    user = get_user_by_id(user_id=user_id, db_session=session)
    ip_address = request.headers.get("X-Forwarded-For", request.client.host)

    # Two limits, checked up front. Wrong codes are counted per email and IP, successful changes per user.
    failed_verification = email_change_verification_rl.check(
        email=user.email, ip=ip_address
    )
    success_attempts = email_change_success_rl.check(user_id=user_id)

    try:
        change_email(
            user=user,
            new_email=body.new_email,
            new_email_code=body.new_email_code,
            current_email_code=body.current_email_code,
            ip_address=ip_address,
            db_session=session,
        )
    except EmailUnchanged:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Currently registered with {body.new_email}.",
        )
    except InvalidEmailOrOTP:
        failed_verification.record()  # Only wrong codes count as failures.
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or passcodes.",
        )
    except EmailAlreadyUsed:
        logger.warning(
            f"User {user_id} tried to switch to an email used by another user."
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already used."
        )

    success_attempts.record()
    logger.info(f"User with id {user_id} successfully changed their email address.")

    # Revoke every existing session so no old token survives the email change,
    # then start a fresh one.
    revoke_all_user_sessions(user_id=user_id)
    response = APIResponse(
        content=AuthResponse(
            token=create_access_token(user_id=user_id),
        ).model_dump()
    )
    set_refresh_token_cookie(
        response, refresh_token=create_refresh_token(user_id=user_id)
    )
    return response
