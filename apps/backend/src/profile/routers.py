import logging

from fastapi import APIRouter, HTTPException, status

from src.auth.dependencies import AuthSessionDep, AuthUserId
from src.auth.exceptions import UserNotFound
from src.auth.repository import get_user_by_id
from src.profile.exceptions import EmailAlreadyUsed
from src.profile.repository import update_user
from src.profile.schemas import ProfileChangesResponse, UserProfile, UserProfileUpdate

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/me", summary="", description="", response_model=UserProfile)
def read_profile(user_id: AuthUserId, db_session: AuthSessionDep):
    try:
        user = get_user_by_id(user_id=user_id, db_session=db_session)
        return UserProfile.model_validate(user)
    except UserNotFound:
        logger.warning(f"User with the id {user_id} not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )


@router.patch("/me", summary="", description="")
def update_profile(
    updated_info: UserProfileUpdate, user_id: AuthUserId, db_session: AuthSessionDep
):
    try:
        report = update_user(
            user_id=user_id, updated_info=updated_info, db_session=db_session
        )
        print(report)
    except UserNotFound:
        logger.warning(f"User with the id {user_id} not found.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found."
        )
    except EmailAlreadyUsed:
        logger.warning(
            f"User with the id {user_id} attempted to switch to an email address "
            f"that is currently used by another user."
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already used."
        )
