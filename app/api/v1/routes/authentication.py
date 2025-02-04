from fastapi import (
    APIRouter,
    Depends,
    status,
    Response,
    Request,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.authentication import (
    validate_credentials,
    get_active_auth_user_info,
    get_device_info,
    get_valid_refresh_token_payload,
)
from app.api.exceptions.authentication import (
    UsernameAlreadyExistsError,
    EmailAlreadyExistsError,
)
from app.services.auth import (
    hash_password,
    create_access_token,
    create_refresh_token,
    get_token_iat_and_exp,
    TokenType,
)
from app.db import get_db_session
from app.exceptions.user import UsernameAlreadyExists, EmailAlreadyExists
from app.models import UserModel
from app.schemes.device_info import SDeviceInfo
from app.schemes.user import SUserSignUp, SUserShortInfo
from app.services.refresh_token import (
    add_refresh_token_to_db, delete_refresh_token_from_db,
)
from app.services.user import create_user

router = APIRouter()


@router.post(
    "/login/",
    summary="Authenticate a user",
)
async def login(
    response: Response,
    user: UserModel = Depends(validate_credentials),
    device_info: SDeviceInfo = Depends(get_device_info),
    db_session: AsyncSession = Depends(get_db_session),
):
    payload = {"sub": user.username}
    access_token_iat_exp = get_token_iat_and_exp(TokenType.ACCESS)
    refresh_token_iat_exp = get_token_iat_and_exp(TokenType.REFRESH)
    access_token = create_access_token(
        payload=payload,
        iat=access_token_iat_exp["iat"],
        expire=access_token_iat_exp["exp"],
    )
    refresh_token = create_refresh_token(
        payload,
        iat=refresh_token_iat_exp["iat"],
        expire=refresh_token_iat_exp["exp"],
    )
    await add_refresh_token_to_db(
        db_session,
        refresh_token,
        user.id,
        refresh_token_iat_exp["iat"],
        refresh_token_iat_exp["exp"],
        device_info,
    )
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
) -> SUserShortInfo:
    user.password = hash_password(user.password.decode())
    try:
        user_from_db = await create_user(user, db_session)
    except UsernameAlreadyExists:
        raise UsernameAlreadyExistsError()
    except EmailAlreadyExists:
        raise EmailAlreadyExistsError()
    return SUserShortInfo.model_validate(user_from_db)


@router.post(
    "/refresh/",
    summary="Release a new access token using refresh token",
)
async def refresh_access_token(
    response: Response,
    payload: dict = Depends(get_valid_refresh_token_payload),
):
    access_token_payload = {"sub": payload.get("sub")}
    access_token_iat_exp = get_token_iat_and_exp(TokenType.ACCESS)
    access_token = create_access_token(
        payload=access_token_payload,
        iat=access_token_iat_exp["iat"],
        expire=access_token_iat_exp["exp"],
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax"
    )
    return {
        "release_new_access_token": "Success!",
    }


@router.post(
    "/logout/",
    summary="Finish the user session",
)
async def logout(
    request: Request,
    response: Response,
    db_session: AsyncSession = Depends(get_db_session),
):
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        await delete_refresh_token_from_db(db_session, refresh_token)
    response.delete_cookie(key="refresh_token")
    response.delete_cookie(key="access_token")
    return {
        "logout": "Success!",
    }


@router.get(
    "/me/",
    summary="Get current user info",
)
async def auth_user_get_info(
    user: UserModel = Depends(get_active_auth_user_info),
) -> SUserShortInfo:
    return SUserShortInfo.model_validate(user)
