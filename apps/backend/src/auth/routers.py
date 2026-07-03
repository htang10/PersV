from fastapi import HTTPException, Request, status
from fastapi.responses import Response
from fastapi.routing import APIRouter

from src.auth.dependencies import AuthSessionDep
from src.auth.exceptions import InvalidCode, UserNotFound
from src.auth.repository import create_user, get_user_by_email, update_login_metadata
from src.auth.schemas import TokenResponse
from src.auth.service.otp import delete_code, verify_code
from src.auth.service.tokens import create_access_token, create_refresh_token
from src.auth.tasks import send_login_otp_task
from src.auth.utils import normalize_email

router = APIRouter()


@router.post(
    "/generate-otp",
    summary="Request a one-time password",
    description="""Sends a time-limited one-time password to the provided email address.
    Use the returned code with POST /login to authenticate.""",
)
def generate_otp(email: str) -> Response:
    normalize_email(email)
    send_login_otp_task.delay(email)

    return Response(
        content=f"Confirmation code has been sent to {email}.",
        status_code=status.HTTP_200_OK,
    )


@router.post(
    "/login",
    summary="Authenticate with a one-time password",
    description="""Verifies the one-time password sent to the provided email.
    Creates a new account if the email is unrecognized. 
    Returns a JWT access token and refresh token on success.""",
)
def login(
    email: str, code: str, request: Request, session: AuthSessionDep
) -> TokenResponse:
    try:
        verify_code(email, code)
        delete_code(email)
    except InvalidCode:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email or passcode."
        )

    try:  # Login
        user = get_user_by_email(email, session)
    except UserNotFound:  # Sign-up
        user = create_user(email, session)

    ip_address = request.headers.get("X-Forwarded-For", request.client.host)
    update_login_metadata(user, ip_address, session)

    return TokenResponse(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
        token_type="bearer",
    )
