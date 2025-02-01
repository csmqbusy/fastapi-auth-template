from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Response,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.authentication import (
    validate_credentials,
    get_refresh_token_payload,
    get_active_auth_user_info,
    get_device_info,
    get_valid_refresh_token_payload,
)
from app.api.exceptions.authentication import (
    UsernameAlreadyExistsError,
    EmailAlreadyExistsError,
)
from app.auth.utils import (
    hash_password,
    create_access_token,
    create_refresh_token,
)
from app.db import get_db_session
from app.exceptions.user import UsernameAlreadyExists, EmailAlreadyExists
from app.models import UserModel
from app.schemes.user import SUserSignUp
from app.services.user import create_user

router = APIRouter()


@router.post(
    "/login/",
    summary="Authenticate a user",
)
async def login(
    request: Request,
    response: Response,
    user: UserModel = Depends(validate_credentials),
    device_info: SDeviceInfo = Depends(get_device_info),
    db_session: AsyncSession = Depends(get_db_session),
):
    payload = {"sub": user.username}
    access_token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax"
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax"
    )

    return {
        "sign_in": "Success!",
    }


@router.post(
    "/registration/",
    summary="Create new user",
    status_code=status.HTTP_201_CREATED,
)
async def sign_up_user(
    user: SUserSignUp,
    db_session: AsyncSession = Depends(get_db_session),
):
    user.password = hash_password(user.password.decode())
    try:
        await create_user(user, db_session)
    except UsernameAlreadyExists:
        raise UsernameAlreadyExistsError()
    except EmailAlreadyExists:
        raise EmailAlreadyExistsError()


@router.post(
    "/refresh/",
    summary="Release a new access token using refresh token",
)
async def refresh_access_token(
    response: Response,
    payload: dict = Depends(get_refresh_token_payload),
):
    access_token_payload = {"sub": payload.get("sub")}
    access_token = create_access_token(access_token_payload)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax"
    )


@router.post(
    "/logout/",
    summary="Finish the user session",
)
async def logout(
    response: Response,
):
    response.delete_cookie(key="refresh_token")
    response.delete_cookie(key="access_token")


@router.get(
    "/me/",
    summary="Get current user info",
)
async def auth_user_get_info(
    user: SUserSignUp = Depends(get_active_auth_user_info),
):
    return {
        "username": user.username,
        "email": user.email,
    }
