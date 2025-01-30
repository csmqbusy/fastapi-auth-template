from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Response,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.authentication import validate_credentials
from app.auth.utils import (
    hash_password,
    create_access_token, create_refresh_token,
)
from app.db import get_db_session
from app.exceptions.user import UsernameAlreadyExists, EmailAlreadyExists
from app.schemas.user import SUserSignUp, SUserSignIn
from app.services.user_service import create_user

router = APIRouter()


@router.post(
    "/login",
    summary="Authenticate a user",
)
async def auth_user_issue_jwt(
    response: Response,
    user: SUserSignIn = Depends(validate_credentials),
):
    payload = {"sub": user.username}
    access_token = create_access_token(payload)
    refresh_token = create_refresh_token(payload)
    response.set_cookie(
        key="access_token", value=access_token, httponly=True, secure=True,
        samesite="lax"
        )
    response.set_cookie(
        key="refresh_token", value=refresh_token, httponly=True
        )
    return {"sign_in": "Success!"}


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
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists.",
        )
    except EmailAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists.",
        )
