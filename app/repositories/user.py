from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import UserModel
from app.schemas.user import SUserSignUp


async def get_user_by_params(
    session: AsyncSession,
    params: dict,
) -> UserModel | None:
    query = select(UserModel).filter_by(**params)
    user = (await session.execute(query)).scalar_one_or_none()
    return user


async def add_user(user: SUserSignUp, session: AsyncSession) -> None:
    stmt = insert(UserModel).values(**user.model_dump())
    await session.execute(stmt)
    await session.commit()
