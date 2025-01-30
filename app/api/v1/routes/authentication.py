from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.utils import (
    hash_password,
)
from app.db import get_db_session
from app.exceptions.user import UsernameAlreadyExists, EmailAlreadyExists
from app.schemas.user import SUserSignUp
from app.services.user_service import create_user

router = APIRouter()


@router.post(
    "/registration/",
    summary="Create new user.",
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
